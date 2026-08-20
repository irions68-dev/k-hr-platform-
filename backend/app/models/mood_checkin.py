from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_USER
from app.core.db import Base

MOOD_VALUES = ("great", "good", "okay", "tired", "stressed")


class MoodCheckin(Base):
    """하루 한 번, 오늘 기분을 가볍게 기록. 홈 화면 위로 문구·연속기록일수 계산에 쓰인다."""

    __tablename__ = "mood_checkins"
    __table_args__ = (UniqueConstraint("created_by", "checkin_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    checkin_date: Mapped[date] = mapped_column(Date)
    mood: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
