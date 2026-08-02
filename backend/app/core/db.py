from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "k_hr.db"
# 컨테이너 배포 시 영구 디스크 경로로 옮기고 싶으면 DB_PATH env var로 override
DB_PATH = Path(os.environ.get("DB_PATH", str(_DEFAULT_DB_PATH)))
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401  모델 등록을 위해 import

    Base.metadata.create_all(bind=engine)
