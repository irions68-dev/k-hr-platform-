"""고객사 담당자에 대해 메모해둔 특징(대화 내용, 성향 메모 등)을 바탕으로

이번 목적(계약 연장 제안, 단가 조율 등)에 맞는 메일 초안을 만든다.

원안("CRM 위스퍼러")은 "심리적 프로파일링"을 표방했지만, 몇 줄 메모만으로
확정적인 성향 진단을 내놓는 건 근거 없는 확신을 주는 위험한 설계다 - 그래서
approach_notes는 항상 "입력하신 메모에 근거해" 제안하는 형태로 한정하고,
메모에 없는 성향을 단정하지 않도록 프롬프트에 강제한다. message_draft.py와
같은 구조(RAG 불필요, 순수 생성형 글쓰기)를 재사용한다.
"""
from __future__ import annotations

from app.engines.gemini_client import (
    GeminiNotConfiguredError,  # noqa: F401  # re-export for API layer
    GeminiQuotaExceededError,  # noqa: F401  # re-export for API layer
    generate_structured_json,
)

SYSTEM_PROMPT = (
    "너는 인력파견회사 관리팀 담당자를 돕는 B2B 커뮤니케이션 초안 작성 도우미이다. "
    "담당자가 입력한 [고객사 담당자 관련 메모]와 [이번 메일의 목적]을 바탕으로 "
    "다음 세 가지를 작성하라: "
    "1) approach_notes: 입력된 메모에서 실제로 드러난 특징에 근거해서만, 이번 "
    "메일을 어떤 톤·분량·구성으로 쓰는 게 좋을지 짧게 제안하라. 메모에 없는 "
    "성향을 확정적으로 단정하거나 심리 진단처럼 서술하지 말고, '메모하신 "
    "내용으로 보아' 같은 표현으로 근거를 밝혀라. 메모가 부실하면 무리하게 "
    "추측하지 말고 일반적인 비즈니스 예의를 따르라고 안내하라. "
    "2) email_draft: 실제로 그대로 보낼 수 있는 수준의 격식 있는 비즈니스 "
    "이메일 초안. 용건과 목적이 첫 문단에서 명확히 드러나야 한다. "
    "3) key_points: 이 메일에서 강조한 핵심 포인트를 bullet 형태의 짧은 문장 "
    "목록으로 정리하라. "
    "메모나 목적에 없는 구체적 정보(담당자 이름, 금액, 날짜 등)는 추측해서 "
    "채우지 말고 대괄호([담당자명], [단가] 등)로 표시해 담당자가 직접 채우게 "
    "하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "approach_notes": {"type": "string"},
        "email_draft": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["approach_notes", "email_draft", "key_points"],
}


def generate_negotiation_draft(context_notes: str, purpose: str) -> dict:
    prompt = (
        f"[고객사 담당자 관련 메모]\n{context_notes.strip()}\n\n"
        f"[이번 메일의 목적]\n{purpose.strip()}"
    )
    return generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
