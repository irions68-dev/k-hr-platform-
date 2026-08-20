from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_USER
from app.core.db import Base


class WorkLogWeeklyReport(Base):
    """금요일 이후 첫 방문 시 자동 생성되어 저장되는 주간 보고서 스냅샷.

    "이번 주 보고서 만들기" 버튼(즉석 생성, 저장 안 함)과는 별개다 - 이건
    방문할 때마다 다시 만들지 않도록 주(week_start) 단위로 한 번만 생성해
    저장해두고, 나중에 목록에서 꺼내볼 수 있게 한다.
    """

    __tablename__ = "work_log_weekly_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    week_end: Mapped[date] = mapped_column(Date)
    report_text: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
