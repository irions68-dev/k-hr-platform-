from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.schemas.dispatch_worker import DispatchWorkerRiskOut
from app.schemas.study import StudyReviewItemOut


class MorningBrief(BaseModel):
    brief_date: date
    at_risk_workers: list[DispatchWorkerRiskOut]
    due_study_items: list[StudyReviewItemOut]
    total_workers: int
    at_risk_count: int
    due_study_count: int
