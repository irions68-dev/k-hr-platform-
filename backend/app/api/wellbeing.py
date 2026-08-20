from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import wellbeing
from app.schemas.wellbeing import MoodCheckinCreate, TodayWellbeing

router = APIRouter(prefix="/wellbeing", tags=["wellbeing"])


@router.get("/today", response_model=TodayWellbeing)
def today(db: Session = Depends(get_db)) -> dict:
    return wellbeing.get_today_summary(db)


@router.post("/mood", response_model=TodayWellbeing)
def post_mood(payload: MoodCheckinCreate, db: Session = Depends(get_db)) -> dict:
    try:
        wellbeing.record_mood(db, payload.mood, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return wellbeing.get_today_summary(db)
