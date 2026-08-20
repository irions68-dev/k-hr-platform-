"""하루하루 대충 적어둔 업무 메모를 모아서, 필요할 때만 주간/월간 보고서로

가공한다. 메모 저장 자체는 결정론적(그냥 DB에 넣기)이고, 보고서 생성만
LLM을 쓴다 - 격식 있는 문장으로 다듬는 건 사람이 잘 못 미루는 글쓰기라
message_draft.py와 같은 이유로 LLM이 적합하다.

Render 무료플랜은 재배포마다 SQLite가 초기화되므로, 이 데이터가 사라지면
아쉬운 정도가 아니라 손해가 크다 - 그래서 AI 없이도 원본 메모를 그대로
텍스트로 뽑아가는 내보내기 기능을 따로 둔다(수시 백업용).
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_USER
from app.engines.gemini_client import (
    GeminiNotConfiguredError,  # noqa: F401  # re-export for API layer
    GeminiQuotaExceededError,  # noqa: F401  # re-export for API layer
    generate_structured_json,
)
from app.models.work_log_entry import WorkLogEntry

SYSTEM_PROMPT = (
    "너는 인력파견회사 관리팀 담당자를 돕는 업무 보고서 작성 도우미이다. "
    "담당자가 하루하루 대충 적어둔 업무 메모 목록을 받아, 상사나 고객사에게 "
    "제출할 수 있는 격식 있는 업무 보고서 한 편으로 정리하라. "
    "메모에 여러 고객사/근로자 관련 내용이 섞여 있으면 관련 항목끼리 묶어서 "
    "정리하고, 단순 나열이 아니라 자연스러운 문장으로 다듬어라. "
    "메모에 없는 내용은 추측해서 채우지 마라. "
    "메모가 부실하거나 특정 날짜에 기록이 없어도 있는 그대로만 반영하고, "
    "빈 기간이 있다는 사실을 지어내서 언급하지 마라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"report": {"type": "string"}},
    "required": ["report"],
}


def add_entry(db: Session, note: str, user: str = DEFAULT_USER) -> WorkLogEntry:
    entry = WorkLogEntry(entry_date=date.today(), note=note.strip(), created_by=user)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_entries(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    user: str = DEFAULT_USER,
) -> list[WorkLogEntry]:
    query = db.query(WorkLogEntry).filter(WorkLogEntry.created_by == user)
    if start_date:
        query = query.filter(WorkLogEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(WorkLogEntry.entry_date <= end_date)
    return query.order_by(WorkLogEntry.entry_date, WorkLogEntry.created_at).all()


def export_text(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    user: str = DEFAULT_USER,
) -> str:
    """AI 없이 원본 메모를 그대로 텍스트로 뽑는다 - 백업용."""
    entries = list_entries(db, start_date, end_date, user)
    if not entries:
        return "(해당 기간에 기록된 메모가 없습니다.)"
    lines = [f"[{e.entry_date.isoformat()}] {e.note}" for e in entries]
    return "\n".join(lines)


def generate_report(
    db: Session, start_date: date, end_date: date, user: str = DEFAULT_USER
) -> str:
    entries = list_entries(db, start_date, end_date, user)
    if not entries:
        return "해당 기간에 기록된 업무 메모가 없습니다."

    lines = [f"- {e.entry_date.isoformat()}: {e.note}" for e in entries]
    prompt = (
        f"[기간] {start_date.isoformat()} ~ {end_date.isoformat()}\n"
        f"[업무 메모 목록]\n" + "\n".join(lines)
    )
    result = generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
    return result["report"]
