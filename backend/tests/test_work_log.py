import json
from datetime import date, timedelta

from app.engines import gemini_client, work_log
from app.models.work_log_entry import WorkLogEntry


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


def test_add_entry_stores_with_todays_date(client_db):
    entry = work_log.add_entry(client_db, "A사 이력서 5개 전달")
    assert entry.entry_date == date.today()
    assert entry.note == "A사 이력서 5개 전달"
    assert client_db.query(WorkLogEntry).count() == 1


def test_add_entry_strips_whitespace(client_db):
    entry = work_log.add_entry(client_db, "  공백 테스트  ")
    assert entry.note == "공백 테스트"


def test_list_entries_filters_by_date_range(client_db):
    today = date.today()
    client_db.add(WorkLogEntry(entry_date=today - timedelta(days=10), note="오래된 메모"))
    client_db.add(WorkLogEntry(entry_date=today, note="오늘 메모"))
    client_db.commit()

    entries = work_log.list_entries(client_db, start_date=today - timedelta(days=1))
    assert len(entries) == 1
    assert entries[0].note == "오늘 메모"


def test_export_text_without_ai_formats_entries(client_db):
    today = date.today()
    client_db.add(WorkLogEntry(entry_date=today, note="B사 근로자 면담 완료"))
    client_db.commit()

    text = work_log.export_text(client_db)
    assert f"[{today.isoformat()}]" in text
    assert "B사 근로자 면담 완료" in text


def test_export_text_handles_empty_range(client_db):
    text = work_log.export_text(client_db, start_date=date(2020, 1, 1), end_date=date(2020, 1, 2))
    assert "없습니다" in text


def test_generate_report_returns_placeholder_when_no_entries(client_db):
    report = work_log.generate_report(client_db, date(2020, 1, 1), date(2020, 1, 2))
    assert "없습니다" in report


def test_generate_report_calls_gemini_with_entries(client_db, monkeypatch):
    fake_client = _FakeClient({"report": "이번 주 업무 보고서 초안입니다."})
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    today = date.today()
    work_log.add_entry(client_db, "A사 이력서 5개 전달")
    work_log.add_entry(client_db, "C사 계약 연장 협의 완료")

    report = work_log.generate_report(client_db, today, today)

    assert report == "이번 주 업무 보고서 초안입니다."
    prompt = fake_client.models.last_contents
    assert "A사 이력서 5개 전달" in prompt
    assert "C사 계약 연장 협의 완료" in prompt


def test_work_log_api_round_trip(client):
    resp = client.post("/work-log/entries", json={"note": "출근 안내 문자 발송"})
    assert resp.status_code == 200
    assert resp.json()["note"] == "출근 안내 문자 발송"

    resp = client.get("/work-log/entries")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_work_log_api_rejects_empty_note(client):
    resp = client.post("/work-log/entries", json={"note": ""})
    assert resp.status_code == 422


def test_work_log_export_api(client):
    client.post("/work-log/entries", json={"note": "테스트 메모"})
    resp = client.get("/work-log/export")
    assert resp.status_code == 200
    assert "테스트 메모" in resp.json()["text"]


def test_work_log_report_api(client, monkeypatch):
    fake_client = _FakeClient({"report": "완성된 보고서"})
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    today = date.today().isoformat()
    client.post("/work-log/entries", json={"note": "D사 면접 조율"})
    resp = client.post("/work-log/report", json={"start_date": today, "end_date": today})

    assert resp.status_code == 200
    assert resp.json()["report"] == "완성된 보고서"
