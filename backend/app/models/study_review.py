from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.dispatch_worker import DEFAULT_USER


class StudyReviewItem(Base):
    """간격반복(SM-2) 학습 복습 항목."""

    __tablename__ = "study_review_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_note_id: Mapped[int | None] = mapped_column(
        ForeignKey("case_notes.id"), nullable=True
    )
    keyword: Mapped[str] = mapped_column(String(200))
    next_review_date: Mapped[date] = mapped_column(Date)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
