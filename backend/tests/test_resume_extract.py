import json

import pytest

from app.engines import resume_extract

SAMPLE_RESULT = {
    "name": "홍길동",
    "birth_date": "1995-03-01",
    "phone": "010-1234-5678",
    "email": "hong@example.com",
    "address": "서울시 강남구",
    "total_years_experience": 3.5,
    "education": [
        {"school": "한국대학교", "major": "경영학과", "degree": "학사", "status": "졸업"}
    ],
    "career": [{"company": "이전회사", "period": "2022.01~2025.06", "role": "물류관리"}],
    "certifications": ["지게차운전기능사"],
    "languages": [],
    "military_service": "육군 병장 만기전역",
    "desired_position": "물류/창고관리",
    "desired_salary": "3000만원",
    "desired_location": "서울/경기",
    "notes": "",
}


class _FakeResponse:
    def __init__(self, payload: dict):
        self.text = json.dumps(payload, ensure_ascii=False)


class _FakeModels:
    def __init__(self, payload: dict, error: Exception | None = None):
        self._payload = payload
        self._error = error

    def generate_content(self, model, contents, config):
        if self._error:
            raise self._error
        return _FakeResponse(self._payload)


class _FakeClient:
    def __init__(self, payload: dict, error: Exception | None = None):
        self.models = _FakeModels(payload, error)


def test_extract_resume_returns_parsed_fields(monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(resume_extract, "_get_client", lambda: fake_client)

    result = resume_extract.extract_resume(b"fake-image-bytes", "image/jpeg")

    assert result["name"] == "홍길동"
    assert result["total_years_experience"] == 3.5
    assert result["career"][0]["company"] == "이전회사"


def test_extract_resume_rejects_unsupported_mime_type():
    with pytest.raises(resume_extract.UnsupportedFileTypeError):
        resume_extract.extract_resume(b"data", "application/msword")


def test_extract_resume_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr(resume_extract, "_get_client", lambda: _FakeClient(SAMPLE_RESULT))
    too_big = b"x" * (resume_extract.MAX_FILE_SIZE_BYTES + 1)
    with pytest.raises(resume_extract.FileTooLargeError):
        resume_extract.extract_resume(too_big, "image/jpeg")


def test_extract_resume_raises_not_configured_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(resume_extract.GeminiNotConfiguredError):
        resume_extract.extract_resume(b"data", "image/png")


def test_resume_api_round_trip(client, monkeypatch):
    fake_client = _FakeClient(SAMPLE_RESULT)
    monkeypatch.setattr(resume_extract, "_get_client", lambda: fake_client)

    resp = client.post(
        "/resume/extract",
        files={"file": ("resume.jpg", b"fake-bytes", "image/jpeg")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "홍길동"
    assert body["certifications"] == ["지게차운전기능사"]


def test_resume_api_rejects_unsupported_type(client):
    resp = client.post(
        "/resume/extract",
        files={"file": ("resume.doc", b"data", "application/msword")},
    )
    assert resp.status_code == 415
