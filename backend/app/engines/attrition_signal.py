"""근로자와 나눈 최근 대화/메모를 입력하면, 그 텍스트 안에서 실제로 드러난

이탈 신호를 요약해서 면담 준비를 돕는다.

원안("이탈 감지 레이더")은 "이탈 위험도 85%" 같은 정량 점수를 표방했지만,
근거 없는 확신을 주는 숫자는 위험하다고 판단해 스코어링을 아예 빼고
정성적 신호 요약으로 재설계했다(검토 시 사용자에게 전달, 동의 후 진행).
observed_signals는 반드시 입력 텍스트에 실제로 존재하는 근거에서만 뽑고,
확률/점수/확정적 예측("곧 퇴사할 것")을 절대 만들지 않도록 시스템 프롬프트에
강제한다. caution_note에는 이 결과가 예단이나 불이익 조치의 근거로 쓰이면
안 된다는 경고를 매번 담는다.
"""
from __future__ import annotations

from app.engines.gemini_client import (
    GeminiNotConfiguredError,  # noqa: F401  # re-export for API layer
    GeminiQuotaExceededError,  # noqa: F401  # re-export for API layer
    generate_structured_json,
)

SYSTEM_PROMPT = (
    "너는 인력파견회사 현장 관리 매니저를 돕는 면담 준비 도우미이다. "
    "매니저가 근로자와 최근 나눈 대화나 메모해 둔 관찰 내용을 입력하면 "
    "다음을 작성하라: "
    "1) observed_signals: 입력된 텍스트 안에 실제로 존재하는 근거에서만 "
    "뽑은 구체적 관찰 사항 목록(예: '급여 정산 관련 불만을 두 번 언급함'). "
    "텍스트에 없는 내용을 추측해서 만들지 마라. 특별한 신호가 없으면 빈 "
    "목록을 반환하라. "
    "2) suggested_approach: 관찰된 내용에 대해 어떻게 대화를 시작하면 좋을지 "
    "짧게 제안하라. "
    "3) talking_points: 면담 시 자연스럽게 꺼내볼 수 있는 질문·화제를 "
    "목록으로 제시하라. "
    "절대로 하지 말아야 할 것: 이탈/퇴사 확률이나 위험도를 숫자·퍼센트로 "
    "산출하지 마라. '곧 퇴사할 것이다' 같은 확정적 예측을 하지 마라. "
    "근로자의 성격이나 심리를 진단하듯 단정하지 마라. "
    "caution_note에는 이 요약이 확정적 예측이 아니라 대화 준비를 돕기 위한 "
    "참고용 관찰 정리일 뿐이며, 근로자를 예단하거나 인사상 불이익 조치의 "
    "근거로 사용해서는 안 된다는 점을 반드시 명시하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "observed_signals": {"type": "array", "items": {"type": "string"}},
        "suggested_approach": {"type": "string"},
        "talking_points": {"type": "array", "items": {"type": "string"}},
        "caution_note": {"type": "string"},
    },
    "required": [
        "observed_signals",
        "suggested_approach",
        "talking_points",
        "caution_note",
    ],
}


def analyze_signals(conversation_notes: str) -> dict:
    prompt = f"[근로자와의 최근 대화/메모]\n{conversation_notes.strip()}"
    return generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
