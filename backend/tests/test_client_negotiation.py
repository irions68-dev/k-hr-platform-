import json
from datetime import date

from app.engines import client_negotiation, gemini_client

SAMPLE_RESULT = {
    "approach_notes": "메모하신 대로 숫자 중심 소통을 선호하신다고 하니, 핵심 지표 위주로 짧게 구성했습니다.",
    "email_draft": "안녕하세요, 담당자님. 계약 연장 관련하여 핵심 지표를 안내드립니다.",
    "key_points": ["가동률 98%", "지연 이슈 0건", "연장 시 단가 동결"],
}


class _FakeResponse:
    def __init__(self, payload: dict):
        self.text = json.dumps(payload, ensure_ascii=False)


class _FakeModels:
    def __init__(self, payload: dict, error: Exception | None = None):
        self._payload = payload
        self._error = error
        self.last_contents = None

    def generate_content(self, model, contents, config):
        self.last_contents = contents
        if self._error:
            raise self._error
        return _FakeResponse(self._payload)


class _FakeClient:
    def __init__(self, payload: dict, error: Exception | None = None):
        self.models = _FakeModels(payload, error)


def test_generate_negotiation_draft_returns_three_fields(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = client_negotiation.generate_negotiation_draft(
        "숫자와 데이터 중심으로 판단하는 편, 과거 지연 이슈로 예민함", "계약 연장 제안"
    )

    assert result["approach_notes"]
    assert result["email_draft"]
    assert result["key_points"] == SAMPLE_RESULT["key_points"]


def test_generate_negotiation_draft_includes_notes_and_purpose_in_prompt(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    client_negotiation.generate_negotiation_draft("말투가 짧고 직관적임", "단가 조율")

    prompt = fake_client.models.last_contents
    assert "[고객사 담당자 관련 메모]" in prompt
    assert "말투가 짧고 직관적임" in prompt
    assert "[이번 메일의 목적]" in prompt
    assert "단가 조율" in prompt


def test_client_negotiation_api_round_trip(client, monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    resp = client.post(
        "/client-negotiation/draft",
        json={"context_notes": "숫자 중심 선호", "purpose": "계약 연장 제안"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email_draft"] == SAMPLE_RESULT["email_draft"]
    assert body["key_points"] == SAMPLE_RESULT["key_points"]


def test_client_negotiation_api_rejects_empty_notes(client):
    resp = client.post(
        "/client-negotiation/draft", json={"context_notes": "", "purpose": "단가 조율"}
    )
    assert resp.status_code == 422


def test_client_negotiation_api_rejects_empty_purpose(client):
    resp = client.post(
        "/client-negotiation/draft", json={"context_notes": "메모", "purpose": ""}
    )
    assert resp.status_code == 422


def test_client_negotiation_api_returns_429_on_quota_exceeded(client, monkeypatch):
    monkeypatch.setattr(
        client_negotiation,
        "generate_structured_json",
        lambda *a, **kw: (_ for _ in ()).throw(gemini_client.GeminiQuotaExceededError("한도 초과")),
    )

    resp = client.post(
        "/client-negotiation/draft", json={"context_notes": "메모", "purpose": "목적"}
    )
    assert resp.status_code == 429
