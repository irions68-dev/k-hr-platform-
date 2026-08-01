"""파견/도급 리스크 판별 룰 엔진.

법적 기한 및 정량 기준(파견 2년, 주 52시간 등)은 LLM의 확률적 판단에
맡기지 않고 순수 함수로 계산한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class RiskStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


DISPATCH_LIMIT_DAYS = 730  # 파견법상 파견기간 한도 2년
WARNING_THRESHOLD_DAYS = 90
CRITICAL_THRESHOLD_DAYS = 30

STATUTORY_WEEKLY_HOURS = 40
MAX_EXTENSION_HOURS = 12
WEEKLY_HOUR_LIMIT = STATUTORY_WEEKLY_HOURS + MAX_EXTENSION_HOURS  # 52


def check_dispatch_expiration(
    contract_start_date: date, reference_date: date | None = None
) -> dict:
    """파견 계약 시작일 기준 2년 만료 D-Day를 계산한다.

    Args:
        contract_start_date: 파견 계약 시작일.
        reference_date: 기준일(생략 시 오늘). 테스트 및 특정 시점 조회용.
    """
    today = reference_date or date.today()
    limit_date = contract_start_date + timedelta(days=DISPATCH_LIMIT_DAYS)
    d_day = (limit_date - today).days

    if d_day <= CRITICAL_THRESHOLD_DAYS:
        status = RiskStatus.CRITICAL
    elif d_day <= WARNING_THRESHOLD_DAYS:
        status = RiskStatus.WARNING
    else:
        status = RiskStatus.NORMAL

    return {
        "limit_date": limit_date,
        "d_day": d_day,
        "status": status,
    }


def check_weekly_hour_limit(weekly_hours: float) -> dict:
    """주 근로시간이 52시간(기본 40 + 연장 12) 한도를 초과하는지 확인한다."""
    excess_hours = round(max(weekly_hours - WEEKLY_HOUR_LIMIT, 0), 2)
    exceeded = weekly_hours > WEEKLY_HOUR_LIMIT

    return {
        "weekly_hours": weekly_hours,
        "limit_hours": WEEKLY_HOUR_LIMIT,
        "excess_hours": excess_hours,
        "exceeded": exceeded,
        "status": RiskStatus.CRITICAL if exceeded else RiskStatus.NORMAL,
    }


@dataclass
class DisguisedContractingFactors:
    """위장도급(불법파견) 판단을 위한 4대 판단기준 체크리스트.

    고용노동부 '근로자파견의 판단기준에 관한 지침' 4대 기준에 대응한다.
    각 항목이 True일수록 원청의 실질적 지배·개입이 크다는 뜻이며,
    파견(불법파견 소지)에 가까워짐을 의미한다.
    """

    principal_directs_work: bool  # 원청이 작업 배치·순서 등을 직접 지시하는가
    integrated_into_principal_business: bool  # 원청 사업에 실질적으로 편입되어 있는가
    lacks_independent_equipment_or_expertise: bool  # 자체 설비·전문성 없이 원청에 의존하는가
    scope_of_work_not_fixed: bool  # 계약상 업무 범위·목적이 불명확한가


def assess_disguised_contracting_risk(factors: DisguisedContractingFactors) -> dict:
    """위장도급 리스크를 체크리스트 기반으로 점수화한다.

    최종적인 불법파견 여부는 개별 사실관계와 최신 판례에 따라 달라지므로,
    이 함수는 리스크 스코어링만 제공하고 법적 결론을 내리지 않는다.
    """
    checks = [
        factors.principal_directs_work,
        factors.integrated_into_principal_business,
        factors.lacks_independent_equipment_or_expertise,
        factors.scope_of_work_not_fixed,
    ]
    score = sum(checks)

    if score >= 3:
        status = RiskStatus.CRITICAL
    elif score >= 1:
        status = RiskStatus.WARNING
    else:
        status = RiskStatus.NORMAL

    return {
        "score": score,
        "max_score": len(checks),
        "status": status,
        "disclaimer": (
            "본 결과는 4대 판단기준 체크리스트에 따른 참고용 스코어링이며, "
            "최종 불법파견 여부는 개별 사실관계 및 최신 판례 확인이 필요합니다."
        ),
    }


def check_supervisory_intermittent_status(
    has_labor_ministry_approval: bool,
    approval_expiry: date | None,
    reference_date: date | None = None,
) -> dict:
    """감시적·단속적 근로 승인(근로기준법 제63조) 유효성을 확인한다."""
    today = reference_date or date.today()

    if not has_labor_ministry_approval:
        return {
            "status": RiskStatus.CRITICAL,
            "reason": "고용노동부 감단 승인 이력 없음 - 근로시간·휴게·휴일 규정 적용제외 불가",
        }

    if approval_expiry is not None and approval_expiry < today:
        return {
            "status": RiskStatus.CRITICAL,
            "reason": f"감단 승인 만료됨 (만료일: {approval_expiry.isoformat()})",
        }

    return {
        "status": RiskStatus.NORMAL,
        "reason": "감단 승인 유효",
    }
