from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.engines import work_log
from app.schemas.work_log import (
    WorkLogEntryCreate,
    WorkLogEntryOut,
    WorkLogExportResult,
    WorkLogReportRequest,
    WorkLogReportResult,
    WorkLogWeeklyReportOut,
)

router = APIRouter(prefix="/work-log", tags=["work-log"])


@router.post("/entries", response_model=WorkLogEntryOut)
def create_entry(payload: WorkLogEntryCreate, db: Session = Depends(get_db)) -> object:
    return work_log.add_entry(db, payload.note)


@router.get("/entries", response_model=list[WorkLogEntryOut])
def list_entries(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> list:
    return work_log.list_entries(db, start_date, end_date)


@router.get("/export", response_model=WorkLogExportResult)
def export(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return {"text": work_log.export_text(db, start_date, end_date)}


@router.post("/report", response_model=WorkLogReportResult)
def report(payload: WorkLogReportRequest, db: Session = Depends(get_db)) -> dict:
    try:
        text = work_log.generate_report(db, payload.start_date, payload.end_date)
    except work_log.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except work_log.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    return {"report": text}


@router.get("/weekly-report/auto", response_model=WorkLogWeeklyReportOut | None)
def weekly_report_auto(db: Session = Depends(get_db)) -> object:
    try:
        return work_log.ensure_weekly_report(db)
    except work_log.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except work_log.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@router.get("/weekly-report/history", response_model=list[WorkLogWeeklyReportOut])
def weekly_report_history(db: Session = Depends(get_db)) -> list:
    return work_log.list_weekly_reports(db)
