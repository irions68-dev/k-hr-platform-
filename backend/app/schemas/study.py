from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class StudyReviewItemCreate(BaseModel):
    keyword: str
    case_note_id: int | None = None


class StudyReviewItemOut(BaseModel):
    id: int
    case_note_id: int | None
    keyword: str
    next_review_date: date
    interval_days: int
    ease_factor: float
    repetitions: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewSubmission(BaseModel):
    quality: int = Field(ge=0, le=5)
