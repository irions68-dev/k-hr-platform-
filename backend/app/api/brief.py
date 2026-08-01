"""오늘 복습할 학습 항목을 모아서 보여준다.

계산해두는 것과 실제로 매일 보게 되는 것은 다르다 - 열어야만 보이는
대시보드는 결국 안 보게 되므로, 홈 화면에서 바로 확인할 수 있게 한다.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.study_review import StudyReviewItem
from app.schemas.brief import MorningBrief

router = APIRouter(prefix="/brief", tags=["brief"])


@router.get("/morning", response_model=MorningBrief)
def morning_brief(db: Session = Depends(get_db)) -> dict:
    today = date.today()

    due_items = (
        db.query(StudyReviewItem)
        .filter(StudyReviewItem.next_review_date <= today)
        .order_by(StudyReviewItem.next_review_date)
        .all()
    )

    return {
        "brief_date": today,
        "due_study_items": due_items,
        "due_study_count": len(due_items),
    }
