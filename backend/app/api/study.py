from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import spaced_repetition
from app.models.study_review import StudyReviewItem
from app.schemas.study import (
    ReviewSubmission,
    StudyReviewItemCreate,
    StudyReviewItemOut,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/review-items", response_model=StudyReviewItemOut)
def create_review_item(
    payload: StudyReviewItemCreate, db: Session = Depends(get_db)
) -> StudyReviewItem:
    item = StudyReviewItem(
        case_note_id=payload.case_note_id,
        keyword=payload.keyword,
        next_review_date=date.today(),
        interval_days=0,
        ease_factor=spaced_repetition.DEFAULT_EASE_FACTOR,
        repetitions=0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/due", response_model=list[StudyReviewItemOut])
def list_due_items(db: Session = Depends(get_db)) -> list[StudyReviewItem]:
    today = date.today()
    return (
        db.query(StudyReviewItem)
        .filter(StudyReviewItem.next_review_date <= today)
        .order_by(StudyReviewItem.next_review_date)
        .all()
    )


@router.post("/review-items/{item_id}/review", response_model=StudyReviewItemOut)
def submit_review(
    item_id: int, payload: ReviewSubmission, db: Session = Depends(get_db)
) -> StudyReviewItem:
    item = db.get(StudyReviewItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="review item not found")

    result = spaced_repetition.schedule_next_review(
        quality=payload.quality,
        state=spaced_repetition.ReviewState(
            interval_days=item.interval_days,
            ease_factor=item.ease_factor,
            repetitions=item.repetitions,
        ),
    )
    item.interval_days = result["interval_days"]
    item.ease_factor = result["ease_factor"]
    item.repetitions = result["repetitions"]
    item.next_review_date = result["next_review_date"]
    db.commit()
    db.refresh(item)
    return item
