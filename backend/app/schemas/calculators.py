from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.engines.rule_checker import RiskStatus


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


class WeeklyHolidayPayRequest(BaseModel):
    weekly_scheduled_hours: float = Field(gt=0)
    daily_scheduled_hours: float = Field(gt=0)
    hourly_wage: float = Field(gt=0)
    full_attendance: bool = True


class WeeklyHolidayPayResponse(BaseModel):
    eligible: bool
    pay: int
    reason: str


class ComprehensiveWageAdequacyRequest(BaseModel):
    included_overtime_pay: float = Field(ge=0)
    actual_overtime_hours: float = Field(ge=0)
    hourly_wage: float = Field(gt=0)


class ComprehensiveWageAdequacyResponse(BaseModel):
    required_overtime_pay: int
    included_overtime_pay: float
    shortfall: int
    adequate: bool
    status: RiskStatus
    disclaimer: str
