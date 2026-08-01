from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.dispatch_worker import DEFAULT_USER

REFERENCE_SEPARATOR = "|"


class CaseNote(Base):
    """실무 Q&A 케이스 아카이브. study_tag(exam_part/core_keyword/importance)를 함께 저장한다."""

    __tablename__ = "case_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    legal_references: Mapped[str] = mapped_column(Text, default="")  # "|" 구분 문자열
    exam_part: Mapped[str] = mapped_column(String(200), default="")
    core_keyword: Mapped[str] = mapped_column(String(200), default="")
    importance: Mapped[str] = mapped_column(String(20), default="Medium")
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
