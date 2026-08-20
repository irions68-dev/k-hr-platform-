from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_USER
from app.core.db import Base


class WorkLogEntry(Base):
    """하루하루 대충 적어두는 업무 메모. 저장만 하고, 주간/월간 보고서는

    누를 때마다 이걸 모아 LLM으로 즉석 생성한다(저장해두지 않음).
    """

    __tablename__ = "work_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_date: Mapped[date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
