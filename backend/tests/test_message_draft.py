import json
from datetime import date

from app.engines import gemini_client, message_draft

SAMPLE_RESULT = {
    "client_email": "안녕하세요, SK하이닉스 담당자님. 면접 일정을 안내드립니다.",
    "worker_message": "안녕하세요! 내일 오후 2시에 면접이 있어요. 잘 준비해주세요 :)",
    "interviewer_memo": "면접 대상자 3명, 일정: 오후 2시",
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


def test_generate_drafts_returns_three_versions(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = message_draft.generate_drafts("SK하이닉스 면접 일정 안내, 대상자 3명, 내일 오후 2시")

    assert result["client_email"]
    assert result["worker_message"]
    assert result["interviewer_memo"]


def test_generate_drafts_includes_todays_date_for_relative_date_resolution(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    message_draft.generate_drafts("내일 출근 안내")

    prompt = fake_client.models.last_contents
    assert date.today().isoformat() in prompt


def test_generate_drafts_includes_situation_type_when_given(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    message_draft.generate_drafts("계약 1개월 연장", situation_type="계약 갱신")

    prompt = fake_client.models.last_contents
    assert "[상황 유형] 계약 갱신" in prompt
    assert "[상황 설명] 계약 1개월 연장" in prompt


def test_generate_drafts_omits_situation_type_section_when_blank(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    message_draft.generate_drafts("출근 안내")

    prompt = fake_client.models.last_contents
    assert "[상황 유형]" not in prompt


def test_message_draft_api_round_trip(client, monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    resp = client.post(
        "/messages/draft",
        json={"situation": "면접 일정 안내", "situation_type": "면접 확정"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_email"] == SAMPLE_RESULT["client_email"]
    assert body["worker_message"] == SAMPLE_RESULT["worker_message"]
    assert body["interviewer_memo"] == SAMPLE_RESULT["interviewer_memo"]


def test_message_draft_api_rejects_empty_situation(client):
    resp = client.post("/messages/draft", json={"situation": ""})
    assert resp.status_code == 422


def test_message_draft_api_returns_429_on_quota_exceeded(client, monkeypatch):
    fake_client = _FakeClient(
        SAMPLE_RESULT, error=gemini_client.GeminiQuotaExceededError("한도 초과")
    )
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)
    # generate_structured_json은 errors.ClientError만 429로 변환하므로,
    # 여기서는 gemini_client 계층의 예외를 그대로 전파하는지 확인하기 위해
    # generate_structured_json 자체를 모킹한다.
    monkeypatch.setattr(
        message_draft,
        "generate_structured_json",
        lambda *a, **kw: (_ for _ in ()).throw(gemini_client.GeminiQuotaExceededError("한도 초과")),
    )

    resp = client.post("/messages/draft", json={"situation": "출근 안내"})
    assert resp.status_code == 429
