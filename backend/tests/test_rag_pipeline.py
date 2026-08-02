import hashlib
from pathlib import Path

import pytest

from app.engines.rag import corpus, generation, pipeline
from app.engines.rag.vector_store import VectorStore


def _fake_embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Gemini API를 실제로 호출하지 않는 결정적(deterministic) 가짜 임베딩.

    이 파일의 테스트들은 파이프라인 로직(인용검증 등)만 검증하고 검색
    순위 품질은 다루지 않으므로, 텍스트마다 고정된 벡터만 나오면 충분하다.
    """
    return [
        [b / 255 for b in hashlib.sha256(text.encode()).digest()[:16]] for text in texts
    ]


@pytest.fixture(autouse=True)
def _mock_gemini_embeddings(monkeypatch):
    monkeypatch.setattr(
        "app.engines.rag.vector_store.embed_texts", _fake_embed_texts
    )


@pytest.fixture()
def seeded_store(tmp_path: Path) -> VectorStore:
    store = VectorStore(persist_dir=tmp_path / "chroma")
    corpus.ingest_sample_corpus(store)
    return store


@pytest.fixture()
def minimal_store(tmp_path: Path) -> VectorStore:
    """단일 문서만 담은 스토어 - 실제 코퍼스의 검색 순위 변동과 무관하게

    파이프라인의 인용검증 로직 자체만 독립적으로 테스트하기 위함
    (코퍼스가 커지면서 특정 질의의 top-k 순위가 바뀌어 이 테스트가
    깨진 적이 있음 - 검색 품질 테스트는 test_corpus.py 등에서 별도로 함).
    """
    store = VectorStore(persist_dir=tmp_path / "chroma")
    store.add_documents(
        ids=["dispatch-law-art6"],
        texts=["파견근로자보호 등에 관한 법률 제6조: 파견기간은 2년을 초과할 수 없다."],
        metadatas=[{"citation": "파견근로자보호 등에 관한 법률 제6조"}],
    )
    return store


def test_ask_returns_grounded_answer_with_verified_citation(minimal_store, monkeypatch):
    def fake_generate(question, context_chunks):
        assert context_chunks  # 검색된 근거가 실제로 프롬프트에 전달되는지 확인
        return {
            "answer": "파견기간은 최대 2년입니다.",
            "legal_references": ["파견근로자보호 등에 관한 법률 제6조"],
            "study_tag": {
                "exam_part": "노동법 제2부",
                "core_keyword": "파견기간",
                "importance": "High",
            },
        }

    monkeypatch.setattr(generation, "generate_grounded_answer", fake_generate)

    result = pipeline.ask("파견 근로자를 얼마나 오래 쓸 수 있어?", store=minimal_store)

    assert result["answer"] == "파견기간은 최대 2년입니다."
    assert result["legal_references"] == ["파견근로자보호 등에 관한 법률 제6조"]
    assert result["rejected_references"] == []
    assert result["study_tag"]["core_keyword"] == "파견기간"
    assert "파견근로자보호 등에 관한 법률 제6조" in result["retrieved_citations"]


def test_ask_rejects_hallucinated_citation_not_in_retrieved_chunks(
    seeded_store, monkeypatch
):
    def fake_generate(question, context_chunks):
        return {
            "answer": "아무 근거 없이 지어낸 답변입니다.",
            "legal_references": ["존재하지않는특별법 제100조"],
            "study_tag": {"exam_part": "", "core_keyword": "", "importance": "Low"},
        }

    monkeypatch.setattr(generation, "generate_grounded_answer", fake_generate)

    result = pipeline.ask("연차휴가는 며칠이야?", store=seeded_store)

    assert result["legal_references"] == ["행정해석 확인 필요"]
    assert result["rejected_references"] == ["존재하지않는특별법 제100조"]


def test_ask_with_empty_store_returns_notice_without_calling_llm(tmp_path, monkeypatch):
    empty_store = VectorStore(persist_dir=tmp_path / "empty_chroma")

    def fail_if_called(question, context_chunks):
        raise AssertionError("검색 결과가 없으면 LLM을 호출하면 안 됨")

    monkeypatch.setattr(generation, "generate_grounded_answer", fail_if_called)

    result = pipeline.ask("아무 질문", store=empty_store)

    assert result["legal_references"] == ["행정해석 확인 필요"]
    assert result["study_tag"] is None
