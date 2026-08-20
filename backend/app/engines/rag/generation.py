"""Gemini API를 통한 근거 기반(grounded) 답변 생성.

시스템 프롬프트는 스펙 문서의 템플릿을 그대로 따르며, 검색된 근거 조문을
반드시 인용하도록 강제한다. 클라이언트 생성·모델명·429/미설정 예외·JSON
파싱은 `gemini_client.py`에 공용으로 모아뒀다 - 모델을 다시 바꿔야 할 때
(gemini-2.5-flash가 신규 사용자에게 차단되어 gemini-3.5-flash로 옮겼던 것
처럼) 거기 한 곳만 고치면 된다.
"""
from __future__ import annotations

from app.engines.gemini_client import (
    DEFAULT_MODEL_NAME as MODEL_NAME,
    GeminiNotConfiguredError,
    GeminiQuotaExceededError,
    generate_structured_json,
)

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


def generate_grounded_answer(question: str, context_chunks: list[str]) -> dict:
    context = "\n\n".join(context_chunks)
    prompt = f"[Vector DB 근거 조문 및 판례]\n{context}\n\n[사용자 질문]\n{question}"
    return generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
