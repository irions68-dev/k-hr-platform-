import hashlib
from pathlib import Path

import pytest

from app.engines import complaint_defense
from app.engines.rag.vector_store import VectorStore


def _fake_embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """test_rag_pipeline.py와 동일한 결정적 가짜 임베딩."""
    return [
        [b / 255 for b in hashlib.sha256(text.encode()).digest()[:16]] for text in texts
    ]


@pytest.fixture(autouse=True)
def _mock_gemini_embeddings(monkeypatch):
    monkeypatch.setattr("app.engines.rag.vector_store.embed_texts", _fake_embed_texts)


@pytest.fixture()
def minimal_store(tmp_path: Path) -> VectorStore:
    store = VectorStore(persist_dir=tmp_path / "chroma")
    store.add_documents(
        ids=["labor-standards-art60"],
        texts=["근로기준법 제60조: 연차 유급휴가는 1년간 80% 이상 출근한 근로자에게 부여한다."],
        metadatas=[{"citation": "근로기준법 제60조"}],
    )
    return store


def test_generate_defense_returns_verified_result(minimal_store, monkeypatch):
    def fake_generate(contents, system_instruction, response_schema):
        assert "근로자 민원 원문" in contents
        return {
            "defense_response": "안녕하세요. 무단결근에 따른 연차 차감은 제60조에 근거한 정당한 처리입니다.",
            "legal_basis": ["근로기준법 제60조"],
            "legal_basis_explanation": "제60조에 따라 출근율 기준으로 연차가 산정됩니다.",
            "caution_note": "감정적으로 대응하지 마세요. 참고용 초안이며 전문가 확인이 필요합니다.",
        }

    monkeypatch.setattr(complaint_defense, "generate_structured_json", fake_generate)

    result = complaint_defense.generate_defense(
        "오늘 갑자기 무단결근해놓고 왜 월차 차감하냐고 항의하는 카톡", store=minimal_store
    )

    assert result["defense_response"]
    assert result["legal_basis"] == ["근로기준법 제60조"]
    assert result["caution_note"]


def test_generate_defense_rejects_hallucinated_citation(minimal_store, monkeypatch):
    def fake_generate(contents, system_instruction, response_schema):
        return {
            "defense_response": "답변",
            "legal_basis": ["존재하지않는특별법 제100조"],
            "legal_basis_explanation": "근거 없이 지어낸 설명입니다.",
            "caution_note": "유의사항",
        }

    monkeypatch.setattr(complaint_defense, "generate_structured_json", fake_generate)

    result = complaint_defense.generate_defense("아무 민원", store=minimal_store)

    assert result["legal_basis"] == ["행정해석 확인 필요"]


def test_generate_defense_with_empty_store_returns_notice_without_calling_llm(
    tmp_path, monkeypatch
):
    empty_store = VectorStore(persist_dir=tmp_path / "empty_chroma")

    def fail_if_called(contents, system_instruction, response_schema):
        raise AssertionError("검색 결과가 없으면 LLM을 호출하면 안 됨")

    monkeypatch.setattr(complaint_defense, "generate_structured_json", fail_if_called)

    result = complaint_defense.generate_defense("아무 민원", store=empty_store)

    assert result["legal_basis"] == ["행정해석 확인 필요"]
    assert result["defense_response"] == ""


def test_complaint_defense_api_round_trip(client, monkeypatch):
    def fake_generate_defense(complaint_text):
        return {
            "defense_response": "답변 초안",
            "legal_basis": ["행정해석 확인 필요"],
            "legal_basis_explanation": "설명",
            "caution_note": "유의사항",
        }

    monkeypatch.setattr(complaint_defense, "generate_defense", fake_generate_defense)

    resp = client.post("/complaint-defense/generate", json={"complaint_text": "민원 텍스트"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["defense_response"] == "답변 초안"


def test_complaint_defense_api_rejects_empty_text(client):
    resp = client.post("/complaint-defense/generate", json={"complaint_text": ""})
    assert resp.status_code == 422
