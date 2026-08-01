"""전화응대용 즉답 계산기 (퇴직금/연차/연장·야간·휴일수당).

파견 근로자가 관리자에게 전화로 가장 자주 묻는 항목들 - 저장 없이
그 자리에서 입력→계산→답변까지 끝내는 것이 목적이다.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from app.engines import rule_checker
from app.schemas.calculators import (
    AnnualLeaveRequest,
    AnnualLeaveResponse,
    OvertimePremiumRequest,
    OvertimePremiumResponse,
    SeverancePayRequest,
    SeverancePayResponse,
)

router = APIRouter(prefix="/calculators", tags=["calculators"])


@router.post("/severance-pay", response_model=SeverancePayResponse)
def severance_pay(payload: SeverancePayRequest) -> dict:
    end_date = payload.resignation_date or date.today()
    tenure_days = (end_date - payload.hire_date).days
    return rule_checker.calculate_severance_pay(payload.average_daily_wage, tenure_days)


@router.post("/annual-leave", response_model=AnnualLeaveResponse)
def annual_leave(payload: AnnualLeaveRequest) -> dict:
    reference = payload.reference_date or date.today()
    tenure_days = (reference - payload.hire_date).days
    return rule_checker.calculate_annual_leave(tenure_days)


@router.post("/overtime-premium", response_model=OvertimePremiumResponse)
def overtime_premium(payload: OvertimePremiumRequest) -> dict:
    return rule_checker.calculate_overtime_premium(
        payload.hourly_wage,
        overtime_hours=payload.overtime_hours,
        night_hours=payload.night_hours,
        holiday_hours=payload.holiday_hours,
    )
