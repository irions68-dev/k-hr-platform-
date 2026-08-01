from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.schemas.study import StudyReviewItemOut


class MorningBrief(BaseModel):
    brief_date: date
    due_study_items: list[StudyReviewItemOut]
    due_study_count: int
