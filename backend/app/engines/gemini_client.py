"""Gemini API 클라이언트 생성 + 구조화된 JSON 생성 공통 로직.

법령 Q&A(rag/generation.py)와 이력서 추출(resume_extract.py)이 각자
클라이언트 생성, 미설정/429 예외, JSON 파싱을 따로 구현하고 있던 걸 한
곳으로 모았다. 모델을 다시 바꿔야 할 때(gemini-2.5-flash가 신규 사용자에게
차단되어 gemini-3.5-flash로 옮겼던 것처럼) 여러 파일을 고칠 필요가 없다.
"""
from __future__ import annotations

import json
import os

from google import genai
from google.genai import errors, types

DEFAULT_MODEL_NAME = "gemini-3.5-flash"

_QUOTA_MESSAGE = (
    "Gemini API 사용 한도를 초과했습니다(이 프로젝트의 다른 AI 기능과 하루 한도를 "
    "공유합니다). 잠시 후 다시 시도하거나 내일 다시 시도하세요."
)


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiQuotaExceededError(RuntimeError):
    """Gemini 무료 티어 일일 호출 한도 초과(429).

    무료 티어는 모델당 하루 요청 수가 제한되어 있다(2026-08-01 기준
    gemini-3.5-flash 무료 티어 하루 20회로 실측 확인). 법령 Q&A·이력서 추출
    등 이 프로젝트의 모든 Gemini 호출 기능이 이 하루 한도를 공유하므로,
    전화응대 도구 특성상 하루 여러 번 쓰다 보면 실제로 부딪힐 수 있는
    제약이다. 500으로 뭉개지 않고 명확히 구분해서 사용자에게 알려준다.
    """


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiNotConfiguredError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
    return genai.Client(api_key=api_key)


def generate_structured_json(
    contents: str | list,
    system_instruction: str,
    response_schema: dict,
    model: str = DEFAULT_MODEL_NAME,
) -> dict:
    """JSON 스키마를 강제한 Gemini 응답을 받아 파싱해서 돌려준다.

    429는 GeminiQuotaExceededError로 변환해서 던진다 - 호출부가 500으로
    뭉개지 않고 명확히 구분해서 사용자에게 보여줄 수 있게.
    """
    client = get_client()
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
    except errors.ClientError as exc:
        if exc.code == 429:
            raise GeminiQuotaExceededError(_QUOTA_MESSAGE) from exc
        raise
    return _normalize_literal_newlines(json.loads(response.text))


def _normalize_literal_newlines(value):
    """Gemini가 가끔 JSON 문자열 안에서 줄바꿈을 이중 이스케이프해서

    (`\\n`을 인코딩해야 할 자리에 `\\\\n`을 내보내) 파싱 후에도 실제 줄바꿈이
    아니라 문자 그대로의 "\\n" 두 글자가 남는 경우가 있다(실측: 업무 로그
    주간 보고서 실제 생성 중 발견). 화면에 백슬래시-n이 그대로 보이는 걸
    막기 위해 모든 문자열 값에서 이 패턴을 실제 줄바꿈으로 정규화한다.
    """
    if isinstance(value, str):
        return value.replace("\\n", "\n")
    if isinstance(value, list):
        return [_normalize_literal_newlines(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_literal_newlines(item) for key, item in value.items()}
    return value
