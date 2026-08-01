from __future__ import annotations

from fastapi import APIRouter

from app.engines import rule_checker
from app.schemas.risk import (
    DisguisedContractingRequest,
    DisguisedContractingResponse,
    DispatchExpirationRequest,
    DispatchExpirationResponse,
    FreelancerMisclassificationRequest,
    FreelancerMisclassificationResponse,
    MonthlyHourExemptionRequest,
    MonthlyHourExemptionResponse,
    SupervisoryStatusRequest,
    SupervisoryStatusResponse,
    WeeklyHourRequest,
    WeeklyHourResponse,
)

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/dispatch-expiration", response_model=DispatchExpirationResponse)
def dispatch_expiration(payload: DispatchExpirationRequest) -> dict:
    return rule_checker.check_dispatch_expiration(payload.contract_start_date)


@router.post("/weekly-hour-limit", response_model=WeeklyHourResponse)
def weekly_hour_limit(payload: WeeklyHourRequest) -> dict:
    return rule_checker.check_weekly_hour_limit(payload.weekly_hours)


@router.post("/disguised-contracting", response_model=DisguisedContractingResponse)
def disguised_contracting(payload: DisguisedContractingRequest) -> dict:
    factors = rule_checker.DisguisedContractingFactors(**payload.model_dump())
    return rule_checker.assess_disguised_contracting_risk(factors)


@router.post("/supervisory-status", response_model=SupervisoryStatusResponse)
def supervisory_status(payload: SupervisoryStatusRequest) -> dict:
    return rule_checker.check_supervisory_intermittent_status(
        payload.has_labor_ministry_approval, payload.approval_expiry
    )


@router.post("/monthly-hour-exemption", response_model=MonthlyHourExemptionResponse)
def monthly_hour_exemption(payload: MonthlyHourExemptionRequest) -> dict:
    return rule_checker.check_monthly_hour_exemption(payload.monthly_hours)


@router.post(
    "/freelancer-misclassification", response_model=FreelancerMisclassificationResponse
)
def freelancer_misclassification(payload: FreelancerMisclassificationRequest) -> dict:
    factors = rule_checker.FreelancerMisclassificationFactors(**payload.model_dump())
    return rule_checker.assess_freelancer_misclassification_risk(factors)
