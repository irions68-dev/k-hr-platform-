from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# 현재는 1인용 도구라 단일 사용자로 고정. 필드 자체는 남겨두어
# 추후 멀티유저로 확장하더라도 스키마 재설계 없이 값만 채우면 되게 한다.
DEFAULT_USER = "default_user"


class DispatchWorker(Base):
    __tablename__ = "dispatch_workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(100))
    contract_start_date: Mapped[date] = mapped_column(Date)
    created_by: Mapped[str] = mapped_column(String(100), default=DEFAULT_USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
