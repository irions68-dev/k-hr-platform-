"""고객사/근로자/면접관에게 보낼 메시지 초안을 한 번에 3종류 생성한다.

법령 Q&A·이력서 추출과 달리 이건 "정답이 정해진 일"이 아니라 상황에 맞게
톤·격식을 바꿔 쓰는 글쓰기라 LLM이 적합하다(계산기류의 "정답 있는 일은
결정론적 로직" 원칙과는 다른 케이스). 단, 실제 발송은 절대 하지 않는다 -
초안만 만들어서 담당자가 검토 후 직접 복사해 보내는 용도.
"""
from __future__ import annotations

from datetime import date

from app.engines.gemini_client import (
    GeminiNotConfiguredError,  # noqa: F401  # re-export for API layer
    GeminiQuotaExceededError,  # noqa: F401  # re-export for API layer
    generate_structured_json,
)

_WEEKDAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]

SYSTEM_PROMPT = (
    "너는 인력파견회사 관리팀 담당자를 돕는 커뮤니케이션 초안 작성 도우미이다. "
    "담당자가 짧게 던진 상황 설명을 바탕으로 서로 다른 대상에게 보낼 초안 3개를 "
    "작성하라: "
    "1) client_email: 고객사 인사담당자에게 보낼 격식 있는 비즈니스 이메일. 존댓말과 "
    "정중한 어조를 쓰고, 용건과 요청사항이 첫 문단에서 명확히 드러나야 한다. "
    "2) worker_message: 파견 근로자에게 보낼 카카오톡/문자 안내 메시지. 친근하지만 "
    "예의 바르고 명확한 어조로, 이메일보다 짧고 간결하게 쓴다. "
    "3) interviewer_memo: 고객사 실무자(면접관)에게 전달할 후보자/상황 요약 메모. "
    "정중하되 이메일보다 실무적이고 간결하게, 핵심 정보를 항목별로 나열한다. "
    "[오늘 날짜]가 주어지니 '내일', '다음주 화요일' 같은 상대적 날짜 표현은 "
    "반드시 그 날짜를 기준으로 실제 날짜(YYYY-MM-DD, 요일 포함)로 환산해서 "
    "초안에 반영하라. "
    "상황 설명에 없는 정보(구체적 이름, 연락처 등)는 추측해서 채우지 말고 "
    "대괄호([담당자명], [연락처] 등)로 표시해 담당자가 직접 채우게 하라. "
    "이 초안은 참고용이며 발송 전 담당자가 검토·수정한다는 전제로, 그대로 써도 "
    "어색하지 않은 자연스러운 수준으로 작성하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "client_email": {"type": "string"},
        "worker_message": {"type": "string"},
        "interviewer_memo": {"type": "string"},
    },
    "required": ["client_email", "worker_message", "interviewer_memo"],
}


def _today_str() -> str:
    today = date.today()
    return f"{today.isoformat()} ({_WEEKDAYS_KO[today.weekday()]}요일)"


def generate_drafts(situation: str, situation_type: str = "") -> dict:
    parts = [f"[오늘 날짜] {_today_str()}"]
    situation_type = situation_type.strip()
    if situation_type:
        parts.append(f"[상황 유형] {situation_type}")
    parts.append(f"[상황 설명] {situation.strip()}")
    prompt = "\n".join(parts)
    return generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
