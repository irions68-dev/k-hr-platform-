from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class WorkLogEntryCreate(BaseModel):
    note: str = Field(min_length=1)


class WorkLogEntryOut(BaseModel):
    id: int
    entry_date: date
    note: str
    created_at: datetime


class WorkLogReportRequest(BaseModel):
    start_date: date
    end_date: date


class WorkLogReportResult(BaseModel):
    report: str


class WorkLogExportResult(BaseModel):
    text: str


class WorkLogWeeklyReportOut(BaseModel):
    id: int
    week_start: date
    week_end: date
    report_text: str
    generated_at: datetime
