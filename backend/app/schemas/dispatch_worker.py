from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.engines.rule_checker import RiskStatus


class DispatchWorkerCreate(BaseModel):
    name: str
    position: str
    contract_start_date: date


class DispatchWorkerOut(BaseModel):
    id: int
    name: str
    position: str
    contract_start_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class DispatchWorkerRiskOut(DispatchWorkerOut):
    limit_date: date
    d_day: int
    status: RiskStatus


class ExcelImportResult(BaseModel):
    imported_count: int
    workers: list[DispatchWorkerOut]
