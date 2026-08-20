import json

from app.engines import attrition_signal, gemini_client

SAMPLE_RESULT = {
    "observed_signals": ["최근 답장이 눈에 띄게 짧아짐", "급여 정산 관련 불만을 두 번 언급함"],
    "suggested_approach": "부담 없이 티타임을 제안하며 급여 이슈부터 편하게 물어보세요.",
    "talking_points": ["요즘 업무는 할 만한지", "급여 정산에서 불편한 점이 있었는지"],
    "caution_note": "이 요약은 확정적 예측이 아니라 대화 준비용 참고 자료이며, 불이익 조치의 근거로 쓰면 안 됩니다.",
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


def test_analyze_signals_returns_grounded_result(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = attrition_signal.analyze_signals("요즘 답장이 짧아졌고, 급여 정산 늦다고 두 번 물어봤어요")

    assert result["observed_signals"] == SAMPLE_RESULT["observed_signals"]
    assert result["suggested_approach"]
    assert result["talking_points"]
    assert result["caution_note"]


def test_analyze_signals_includes_notes_in_prompt(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    attrition_signal.analyze_signals("최근 대화 내용 예시")

    prompt = fake_client.models.last_contents
    assert "[근로자와의 최근 대화/메모]" in prompt
    assert "최근 대화 내용 예시" in prompt


def test_attrition_signal_api_round_trip(client, monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    resp = client.post(
        "/attrition-signal/analyze", json={"conversation_notes": "대화 메모"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["observed_signals"] == SAMPLE_RESULT["observed_signals"]
    assert body["caution_note"]


def test_attrition_signal_api_rejects_empty_notes(client):
    resp = client.post("/attrition-signal/analyze", json={"conversation_notes": ""})
    assert resp.status_code == 422


def test_attrition_signal_api_returns_429_on_quota_exceeded(client, monkeypatch):
    monkeypatch.setattr(
        attrition_signal,
        "generate_structured_json",
        lambda *a, **kw: (_ for _ in ()).throw(gemini_client.GeminiQuotaExceededError("한도 초과")),
    )

    resp = client.post("/attrition-signal/analyze", json={"conversation_notes": "메모"})
    assert resp.status_code == 429
