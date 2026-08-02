"""Gemini API를 통한 근거 기반(grounded) 답변 생성.

시스템 프롬프트는 스펙 문서의 템플릿을 그대로 따르며, 검색된 근거 조문을
반드시 인용하도록 강제한다. 모델은 별칭(-latest)이 아닌 고정 버전 문자열을
사용한다 - 별칭이 교체되면서 400 에러가 났던 과거 사례를 반복하지 않기 위함.
단, 고정 버전도 구글 쪽에서 구모델을 신규 사용자에게 차단하는 등 예고 없이
바뀔 수 있으므로, 404/400 에러가 나면 `client.models.list()`로 현재 사용
가능한 모델 목록을 먼저 확인할 것 (2026-08-01 기준 gemini-2.5-flash는
신규 사용자에게 차단되어 gemini-3.5-flash로 교체함).
"""
from __future__ import annotations

import json
import os

from google import genai
from google.genai import errors, types

MODEL_NAME = "gemini-3.5-flash"

SYSTEM_PROMPT = (
    "너는 파견회사 전문 노무 AI 어시스턴트이다. 사용자의 질문에 답변할 때 "
    "반드시 검색된 [Vector DB 근거 조문 및 판례]를 인용하여 답변하라. "
    "확실한 근거가 없는 내용은 추측하여 답변하지 말고 "
    "'행정해석 확인 필요'를 명시하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "legal_references": {"type": "array", "items": {"type": "string"}},
        "study_tag": {
            "type": "object",
            "properties": {
                "exam_part": {"type": "string"},
                "core_keyword": {"type": "string"},
                "importance": {"type": "string", "enum": ["High", "Medium", "Low"]},
            },
            "required": ["exam_part", "core_keyword", "importance"],
        },
    },
    "required": ["answer", "legal_references", "study_tag"],
}


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiQuotaExceededError(RuntimeError):
    """Gemini 무료 티어 일일/분당 호출 한도 초과 (429).

    무료 티어는 모델당 하루 요청 수가 제한되어 있다(2026-08-01 기준
    gemini-3.5-flash 무료 티어 하루 20회로 실측 확인). 전화응대 도구 특성상
    하루 여러 번 쓰다 보면 실제로 부딪힐 수 있는 제약이라 500으로 뭉개지
    않고 명확히 구분해서 알려준다.
    """


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiNotConfiguredError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")
    return genai.Client(api_key=api_key)


def generate_grounded_answer(question: str, context_chunks: list[str]) -> dict:
    client = _get_client()
    context = "\n\n".join(context_chunks)
    prompt = f"[Vector DB 근거 조문 및 판례]\n{context}\n\n[사용자 질문]\n{question}"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
            ),
        )
    except errors.ClientError as exc:
        if exc.code == 429:
            raise GeminiQuotaExceededError(
                "Gemini API 사용 한도를 초과했습니다. 잠시 후 다시 시도하거나 "
                "무료 티어 일일 한도라면 내일 다시 시도하세요."
            ) from exc
        raise

    return json.loads(response.text)
