import json

from app.engines import gemini_client


class _FakeResponse:
    def __init__(self, raw_text: str):
        self.text = raw_text


class _FakeModels:
    def __init__(self, raw_text: str):
        self._raw_text = raw_text

    def generate_content(self, model, contents, config):
        return _FakeResponse(self._raw_text)


class _FakeClient:
    def __init__(self, raw_text: str):
        self.models = _FakeModels(raw_text)


def test_generate_structured_json_normalizes_double_escaped_newlines(monkeypatch):
    # json.dumps로 "\n"(진짜 줄바꿈 1글자)을 넣으면 raw JSON엔 \n 이스케이프가
    # 나오지만, 여기선 실측 버그를 재현하려고 백슬래시 자체를 이스케이프한
    # "\\n"(문자 그대로 \n 두 글자)이 JSON 문자열 안에 들어간 상황을 만든다.
    raw_json = json.dumps({"report": "1문단\\n\\n2문단"}, ensure_ascii=False)
    fake_client = _FakeClient(raw_json)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = gemini_client.generate_structured_json("prompt", "system", {"type": "object"})

    assert result["report"] == "1문단\n\n2문단"
    assert "\\n" not in result["report"]


def test_generate_structured_json_leaves_normal_json_newlines_intact(monkeypatch):
    raw_json = json.dumps({"report": "1문단\n\n2문단"}, ensure_ascii=False)
    fake_client = _FakeClient(raw_json)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = gemini_client.generate_structured_json("prompt", "system", {"type": "object"})

    assert result["report"] == "1문단\n\n2문단"


def test_generate_structured_json_normalizes_nested_lists(monkeypatch):
    raw_json = json.dumps({"items": ["a\\nb", "c"]}, ensure_ascii=False)
    fake_client = _FakeClient(raw_json)
    monkeypatch.setattr(gemini_client, "get_client", lambda: fake_client)

    result = gemini_client.generate_structured_json("prompt", "system", {"type": "object"})

    assert result["items"] == ["a\nb", "c"]
