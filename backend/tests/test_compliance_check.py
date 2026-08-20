import hashlib
from pathlib import Path

import pytest

from app.engines import compliance_check
from app.engines.rag.vector_store import VectorStore


def _fake_embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """test_rag_pipeline.py와 동일한 결정적 가짜 임베딩 - 실제 Gemini 호출 없이

    검색 자체는 동작하게 하되(코사인 유사도 계산 가능), 순위 품질은 안 다룬다.
    """
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
        ids=["dispatch-law-art6"],
        texts=["파견근로자보호 등에 관한 법률 제6조: 파견기간은 2년을 초과할 수 없다."],
        metadatas=[{"citation": "파견근로자보호 등에 관한 법률 제6조"}],
    )
    return store


def test_check_compliance_returns_verified_result(minimal_store, monkeypatch):
    def fake_generate(contents, system_instruction, response_schema):
        assert "고객사 운영 방식 설명" in contents
        return {
            "risk_level": "높음",
            "risk_summary": (
                "제6조에 따르면 파견기간은 2년을 초과할 수 없습니다. 참고용 초안이며 "
                "전문가 확인이 필요합니다."
            ),
            "legal_references": ["파견근로자보호 등에 관한 법률 제6조"],
            "pitch": "당사의 합법적 도급 모델로 전환 시 리스크를 줄일 수 있습니다.",
        }

    monkeypatch.setattr(compliance_check, "generate_structured_json", fake_generate)

    result = compliance_check.check_compliance(
        "3년째 같은 인력을 파견 형태로 계속 사용 중", store=minimal_store
    )

    assert result["risk_level"] == "높음"
    assert result["legal_references"] == ["파견근로자보호 등에 관한 법률 제6조"]
    assert result["pitch"]


def test_check_compliance_rejects_hallucinated_citation(minimal_store, monkeypatch):
    def fake_generate(contents, system_instruction, response_schema):
        return {
            "risk_level": "주의",
            "risk_summary": "근거 없이 지어낸 설명입니다.",
            "legal_references": ["존재하지않는특별법 제100조"],
            "pitch": "",
        }

    monkeypatch.setattr(compliance_check, "generate_structured_json", fake_generate)

    result = compliance_check.check_compliance("아무 상황", store=minimal_store)

    assert result["legal_references"] == ["행정해석 확인 필요"]


def test_check_compliance_with_empty_store_returns_notice_without_calling_llm(
    tmp_path, monkeypatch
):
    empty_store = VectorStore(persist_dir=tmp_path / "empty_chroma")

    def fail_if_called(contents, system_instruction, response_schema):
        raise AssertionError("검색 결과가 없으면 LLM을 호출하면 안 됨")

    monkeypatch.setattr(compliance_check, "generate_structured_json", fail_if_called)

    result = compliance_check.check_compliance("아무 상황", store=empty_store)

    assert result["risk_level"] == "판단 불가"
    assert result["legal_references"] == ["행정해석 확인 필요"]


def test_compliance_api_round_trip(client, monkeypatch):
    def fake_check(situation):
        return {
            "risk_level": "낮음",
            "risk_summary": "요약",
            "legal_references": ["행정해석 확인 필요"],
            "pitch": "피치 문구",
        }

    monkeypatch.setattr(compliance_check, "check_compliance", fake_check)

    resp = client.post("/compliance/check", json={"situation": "도급 형태로 운영 중"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "낮음"
    assert body["pitch"] == "피치 문구"


def test_compliance_api_rejects_empty_situation(client):
    resp = client.post("/compliance/check", json={"situation": ""})
    assert resp.status_code == 422
