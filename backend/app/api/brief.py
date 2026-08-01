"""매일 확인해야 할 것을 한 화면에 모아주는 아침 브리핑.

계산해두는 것과 실제로 매일 보게 되는 것은 다르다 - 열어야만 보이는
대시보드는 결국 안 보게 되므로, 이 엔드포인트 하나로 오늘 챙겨야 할
파견 만료 위험과 학습 복습 항목을 모두 모아서 보여준다.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import rule_checker
from app.models.dispatch_worker import DispatchWorker
from app.models.study_review import StudyReviewItem
from app.schemas.brief import MorningBrief

router = APIRouter(prefix="/brief", tags=["brief"])

AT_RISK_STATUSES = {rule_checker.RiskStatus.WARNING, rule_checker.RiskStatus.CRITICAL}


@router.get("/morning", response_model=MorningBrief)
def morning_brief(db: Session = Depends(get_db)) -> dict:
    today = date.today()

    workers = db.query(DispatchWorker).all()
    at_risk = []
    for worker in workers:
        expiration = rule_checker.check_dispatch_expiration(worker.contract_start_date)
        if expiration["status"] in AT_RISK_STATUSES:
            at_risk.append(
                {
                    "id": worker.id,
                    "name": worker.name,
                    "position": worker.position,
                    "contract_start_date": worker.contract_start_date,
                    "created_at": worker.created_at,
                    "limit_date": expiration["limit_date"],
                    "d_day": expiration["d_day"],
                    "status": expiration["status"],
                }
            )
    at_risk.sort(key=lambda w: w["d_day"])

    due_items = (
        db.query(StudyReviewItem)
        .filter(StudyReviewItem.next_review_date <= today)
        .order_by(StudyReviewItem.next_review_date)
        .all()
    )

    return {
        "brief_date": today,
        "at_risk_workers": at_risk,
        "due_study_items": due_items,
        "total_workers": len(workers),
        "at_risk_count": len(at_risk),
        "due_study_count": len(due_items),
    }
