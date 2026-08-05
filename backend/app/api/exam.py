from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import exam_daily
from app.schemas.exam import (
    DailyQuestion,
    ExamAttemptResult,
    ExamAttemptSubmit,
    ExamStats,
)

router = APIRouter(prefix="/exam", tags=["exam"])


@router.get("/daily", response_model=list[DailyQuestion])
def get_daily_questions(db: Session = Depends(get_db)) -> list[dict]:
    return exam_daily.select_daily_questions(db, count=3)


@router.post("/attempts", response_model=ExamAttemptResult)
def submit_attempt(
    payload: ExamAttemptSubmit, db: Session = Depends(get_db)
) -> dict:
    try:
        return exam_daily.record_attempt(
            db, payload.question_id, payload.selected_index
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/stats", response_model=ExamStats)
def get_stats(db: Session = Depends(get_db)) -> dict:
    return exam_daily.get_stats(db)
