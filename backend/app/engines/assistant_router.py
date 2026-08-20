"""텍스트를 붙여넣기만 하면 어떤 도구가 필요한지 스스로 판단해서

알맞은 엔진으로 라우팅한다("뭐든 붙여넣기" 통합 입력창의 백엔드).

4개의 개별 페이지(민원 방어/컴플라이언스 진단/이탈 신호 노트/멘트 메이커)를
매번 사용자가 직접 골라 들어가야 하는 게 실사용 마찰이라고 판단해 추가한
라우터 계층이다. 고객사 메일 도우미(client_negotiation)는 "메일 목적"이라는
별도 필드가 꼭 필요해서 이 자동분류 대상에서 제외하고 기존 페이지를
그대로 쓴다. 분류에 Gemini 호출을 1번 더 쓰기 때문에(분류 1회 + 실제
생성 1회) 하루 호출 한도를 개별 페이지보다 빨리 소모한다는 트레이드오프가
있다.
"""
from __future__ import annotations

from app.engines import attrition_signal, complaint_defense, compliance_check, message_draft
from app.engines.gemini_client import (
    GeminiNotConfiguredError,  # noqa: F401  # re-export for API layer
    GeminiQuotaExceededError,  # noqa: F401  # re-export for API layer
    generate_structured_json,
)

CATEGORY_LABELS = {
    "complaint_defense": "민원 방어",
    "compliance_check": "컴플라이언스 진단",
    "attrition_signal": "이탈 신호 노트",
    "message_draft": "멘트 메이커",
}

CLASSIFY_SYSTEM_PROMPT = (
    "너는 인력파견회사 관리팀 담당자가 붙여넣은 텍스트를 보고 어떤 도구로 "
    "처리해야 할지 분류하는 라우터이다. 다음 네 가지 중 하나로만 분류하라: "
    "1) complaint_defense: 근로자가 보낸 감정적이거나 공격적인 민원·항의 "
    "텍스트(카톡, 문자 등)로, 사무적인 방어 답변이 필요한 경우. "
    "2) compliance_check: (잠재)고객사가 현재 인력을 운영하는 방식에 대한 "
    "설명으로, 위장도급·불법파견 리스크 진단이 필요한 경우. "
    "3) attrition_signal: 근로자와 나눈 최근 대화나 관찰한 내용으로, 면담 "
    "준비를 위해 눈에 띄는 신호를 정리해야 하는 경우. "
    "4) message_draft: 고객사/근로자/면접관에게 보낼 안내 메시지(면접 확정, "
    "계약 갱신, 출근 안내 등)를 작성해야 하는 일반적인 상황 설명인 경우. "
    "네 가지 중 어디에도 뚜렷하게 맞지 않으면 message_draft를 기본값으로 "
    "선택하라."
)

CLASSIFY_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": list(CATEGORY_LABELS.keys()),
        },
    },
    "required": ["category"],
}

_DISPATCH = {
    "complaint_defense": lambda text: complaint_defense.generate_defense(text),
    "compliance_check": lambda text: compliance_check.check_compliance(text),
    "attrition_signal": lambda text: attrition_signal.analyze_signals(text),
    "message_draft": lambda text: message_draft.generate_drafts(text),
}


def route(text: str) -> dict:
    text = text.strip()
    classification = generate_structured_json(
        text, CLASSIFY_SYSTEM_PROMPT, CLASSIFY_RESPONSE_SCHEMA
    )
    category = classification.get("category", "message_draft")
    if category not in _DISPATCH:
        category = "message_draft"

    result = _DISPATCH[category](text)

    return {
        "category": category,
        "category_label": CATEGORY_LABELS[category],
        "result": result,
    }
