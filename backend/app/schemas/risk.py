from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.engines.rule_checker import RiskStatus


class DispatchExpirationRequest(BaseModel):
    contract_start_date: date


class DispatchExpirationResponse(BaseModel):
    limit_date: date
    d_day: int
    status: RiskStatus


class WeeklyHourRequest(BaseModel):
    weekly_hours: float = Field(gt=0)


class WeeklyHourResponse(BaseModel):
    weekly_hours: float
    limit_hours: float
    excess_hours: float
    exceeded: bool
    status: RiskStatus


class DisguisedContractingRequest(BaseModel):
    principal_directs_work: bool
    integrated_into_principal_business: bool
    lacks_independent_equipment_or_expertise: bool
    scope_of_work_not_fixed: bool


class DisguisedContractingResponse(BaseModel):
    score: int
    max_score: int
    status: RiskStatus
    disclaimer: str


class SupervisoryStatusRequest(BaseModel):
    has_labor_ministry_approval: bool
    approval_expiry: date | None = None


class SupervisoryStatusResponse(BaseModel):
    status: RiskStatus
    reason: str
