from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class SeverancePayRequest(BaseModel):
    hire_date: date
    resignation_date: date | None = None
    average_daily_wage: float = Field(gt=0)


class SeverancePayResponse(BaseModel):
    eligible: bool
    tenure_days: int
    severance_pay: int
    reason: str


class AnnualLeaveRequest(BaseModel):
    hire_date: date
    reference_date: date | None = None


class AnnualLeaveResponse(BaseModel):
    tenure_days: int
    years_of_service: int | None = None
    granted_days: int
    basis: str


class OvertimePremiumRequest(BaseModel):
    hourly_wage: float = Field(gt=0)
    overtime_hours: float = Field(default=0, ge=0)
    night_hours: float = Field(default=0, ge=0)
    holiday_hours: float = Field(default=0, ge=0)


class OvertimePremiumResponse(BaseModel):
    overtime_pay: int
    night_pay: int
    holiday_pay: int
    total_premium_pay: int
