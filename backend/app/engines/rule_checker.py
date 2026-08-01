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

MONTHLY_HOUR_EXEMPTION_THRESHOLD = 60  # 이 미만이면 4대보험(국민연금·건강보험) 적용제외 대상

SEVERANCE_MINIMUM_TENURE_DAYS = 365  # 퇴직금은 계속근로 1년 이상만 지급의무
SEVERANCE_ACCRUAL_DAYS = 30  # 평균임금 30일분

ANNUAL_LEAVE_FIRST_YEAR_CAP = 11  # 1년 미만 근속자의 최대 연차(개근 월 1일씩)
ANNUAL_LEAVE_BASE_DAYS = 15  # 1년 이상 근속자의 기본 연차
ANNUAL_LEAVE_MAX_DAYS = 25  # 가산 포함 상한

OVERTIME_PREMIUM_RATE = 0.5  # 연장·야간근로 가산율
HOLIDAY_PREMIUM_RATE = 0.5  # 휴일근로 8시간 이내 가산율
HOLIDAY_OVER_8H_PREMIUM_RATE = 1.0  # 휴일근로 8시간 초과분 가산율

WEEKLY_HOLIDAY_MIN_HOURS = 15  # 주휴수당 지급을 위한 최소 주 소정근로시간
WEEKLY_HOLIDAY_MAX_DAILY_HOURS = 8  # 주휴수당 산정 시 1일 근로시간 인정 상한


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


def check_monthly_hour_exemption(monthly_hours: float) -> dict:
    """월 소정근로시간이 60시간 미만이면 국민연금·건강보험 적용제외 대상임을 안내한다."""
    exempt = monthly_hours < MONTHLY_HOUR_EXEMPTION_THRESHOLD
    return {
        "monthly_hours": monthly_hours,
        "threshold_hours": MONTHLY_HOUR_EXEMPTION_THRESHOLD,
        "exempt_from_pension_and_health_insurance": exempt,
        "reason": (
            "월 소정근로시간 60시간 미만은 국민연금·건강보험 적용제외 대상"
            if exempt
            else "월 60시간 이상이므로 4대보험 가입대상"
        ),
    }


@dataclass
class FreelancerMisclassificationFactors:
    """위장프리랜서(3.3% 사업소득 처리) 판단을 위한 체크리스트.

    실질은 근로자인데 3.3% 사업소득으로 처리해 4대보험·근로기준법 적용을
    회피하는 경우를 가려내기 위한 참고용 스코어링. 대법원 판례상 근로자성
    판단은 계약형식이 아니라 실질(사용종속관계)을 기준으로 한다.
    """

    fixed_working_hours_and_place: bool  # 근무시간·장소가 지정되어 있는가
    subject_to_direction_and_supervision: bool  # 업무수행 과정에서 지휘·감독을 받는가
    cannot_delegate_or_use_substitute: bool  # 본인이 아닌 제3자에게 대체 수행시킬 수 없는가
    exclusive_and_continuous_engagement: bool  # 특정 사업장에 전속적·계속적으로 종사하는가


def assess_freelancer_misclassification_risk(
    factors: FreelancerMisclassificationFactors,
) -> dict:
    """위장프리랜서(3.3%) 리스크를 체크리스트 기반으로 점수화한다."""
    checks = [
        factors.fixed_working_hours_and_place,
        factors.subject_to_direction_and_supervision,
        factors.cannot_delegate_or_use_substitute,
        factors.exclusive_and_continuous_engagement,
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
            "본 결과는 참고용 스코어링이며, 근로자성(위장프리랜서) 최종 판단은 "
            "개별 사실관계 및 최신 판례 확인이 필요합니다."
        ),
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


NIGHT_PREMIUM_NOTE = (
    "감단(감시·단속적) 승인을 받아도 근로시간·휴게·휴일 규정만 적용제외될 뿐, "
    "야간근로(22:00~06:00) 가산수당(통상임금의 50%)은 별도로 지급해야 한다 "
    "(법제처 법령해석, 근로기준법 제56조는 제63조 적용제외 대상이 아님)."
)


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
            "night_premium_note": NIGHT_PREMIUM_NOTE,
        }

    if approval_expiry is not None and approval_expiry < today:
        return {
            "status": RiskStatus.CRITICAL,
            "reason": f"감단 승인 만료됨 (만료일: {approval_expiry.isoformat()})",
            "night_premium_note": NIGHT_PREMIUM_NOTE,
        }

    return {
        "status": RiskStatus.NORMAL,
        "reason": "감단 승인 유효",
        "night_premium_note": NIGHT_PREMIUM_NOTE,
    }


def calculate_severance_pay(average_daily_wage: float, tenure_days: int) -> dict:
    """퇴직금을 계산한다 (근로기준법 - 평균임금 30일분 × 재직일수/365).

    Args:
        average_daily_wage: 퇴직 전 3개월 평균임금(1일분). 급여대장 등에서 산출된
            값을 그대로 입력받는다 - 이 함수는 평균임금 자체를 산정하지 않는다.
        tenure_days: 입사일부터 퇴사일까지의 재직일수.
    """
    eligible = tenure_days >= SEVERANCE_MINIMUM_TENURE_DAYS
    severance_pay = (
        round(average_daily_wage * SEVERANCE_ACCRUAL_DAYS * (tenure_days / 365))
        if eligible
        else 0
    )
    return {
        "eligible": eligible,
        "tenure_days": tenure_days,
        "severance_pay": severance_pay,
        "reason": (
            "계속근로기간 1년 이상 - 지급 대상"
            if eligible
            else "계속근로기간 1년 미만 - 퇴직금 지급의무 없음"
        ),
    }


def calculate_annual_leave(tenure_days: int) -> dict:
    """연차유급휴가 발생 일수를 계산한다 (근로기준법 제60조).

    1년 미만: 1개월 개근마다 1일(최대 11일).
    1년 이상: 15일 + (근속연수-1)//2 가산, 최대 25일.
    """
    if tenure_days < 365:
        months_worked = tenure_days // 30
        granted_days = min(months_worked, ANNUAL_LEAVE_FIRST_YEAR_CAP)
        return {
            "tenure_days": tenure_days,
            "granted_days": granted_days,
            "basis": "1년 미만 - 1개월 개근시 1일씩 발생(최대 11일)",
        }

    years_of_service = tenure_days // 365
    extra_days = (years_of_service - 1) // 2
    granted_days = min(ANNUAL_LEAVE_BASE_DAYS + extra_days, ANNUAL_LEAVE_MAX_DAYS)
    return {
        "tenure_days": tenure_days,
        "years_of_service": years_of_service,
        "granted_days": granted_days,
        "basis": "1년 이상 - 기본 15일 + 최초 1년 초과 매 2년당 1일 가산(최대 25일)",
    }


def calculate_overtime_premium(
    hourly_wage: float,
    overtime_hours: float = 0,
    night_hours: float = 0,
    holiday_hours: float = 0,
) -> dict:
    """연장·야간·휴일근로수당을 계산한다 (근로기준법 제56조, 가산율 50%/100%).

    Args:
        hourly_wage: 통상시급.
        overtime_hours: 연장근로시간(법정 근로시간 초과분).
        night_hours: 야간근로시간(22:00~06:00).
        holiday_hours: 휴일근로시간(8시간 이내 50%, 초과분 100% 자동 적용).
    """
    holiday_normal = min(holiday_hours, 8)
    holiday_over_8 = max(holiday_hours - 8, 0)

    overtime_pay = round(hourly_wage * (1 + OVERTIME_PREMIUM_RATE) * overtime_hours)
    night_pay = round(hourly_wage * (1 + OVERTIME_PREMIUM_RATE) * night_hours)
    holiday_pay = round(
        hourly_wage * (1 + HOLIDAY_PREMIUM_RATE) * holiday_normal
        + hourly_wage * (1 + HOLIDAY_OVER_8H_PREMIUM_RATE) * holiday_over_8
    )

    return {
        "overtime_pay": overtime_pay,
        "night_pay": night_pay,
        "holiday_pay": holiday_pay,
        "total_premium_pay": overtime_pay + night_pay + holiday_pay,
    }


def calculate_weekly_holiday_pay(
    weekly_scheduled_hours: float,
    daily_scheduled_hours: float,
    hourly_wage: float,
    full_attendance: bool = True,
) -> dict:
    """주휴수당을 계산한다 (근로기준법 제55조).

    지급 요건: 1주 소정근로시간 15시간 이상 + 소정근로일 개근.
    금액: min(1일 소정근로시간, 8시간) × 시급. 물류·서비스직의 일용·단시간
    근로자에게 가장 자주 발생하는 문의 중 하나다.
    """
    if weekly_scheduled_hours < WEEKLY_HOLIDAY_MIN_HOURS:
        return {
            "eligible": False,
            "pay": 0,
            "reason": (
                f"주 소정근로시간 {weekly_scheduled_hours}시간이 "
                f"{WEEKLY_HOLIDAY_MIN_HOURS}시간 미만 - 지급 대상 아님"
            ),
        }

    if not full_attendance:
        return {
            "eligible": False,
            "pay": 0,
            "reason": "소정근로일 개근하지 않음 - 지급 대상 아님",
        }

    recognized_hours = min(daily_scheduled_hours, WEEKLY_HOLIDAY_MAX_DAILY_HOURS)
    pay = round(recognized_hours * hourly_wage)

    return {
        "eligible": True,
        "pay": pay,
        "reason": "주 15시간 이상 + 개근 - 지급 대상",
    }


def assess_comprehensive_wage_adequacy(
    included_overtime_pay: float,
    actual_overtime_hours: float,
    hourly_wage: float,
) -> dict:
    """포괄임금제에 포함된 연장근로수당이 실제 연장근로시간을 커버하는지 검토한다.

    포괄임금제 자체가 위법은 아니지만, 실제 연장근로에 대한 법정 가산수당보다
    적게 포함되어 있으면 그 차액은 별도로 지급해야 한다(대법원 판례상
    포괄임금 약정도 근로기준법 최저기준을 하회할 수 없음).
    """
    required_overtime_pay = round(hourly_wage * (1 + OVERTIME_PREMIUM_RATE) * actual_overtime_hours)
    shortfall = max(required_overtime_pay - included_overtime_pay, 0)

    return {
        "required_overtime_pay": required_overtime_pay,
        "included_overtime_pay": included_overtime_pay,
        "shortfall": shortfall,
        "adequate": shortfall == 0,
        "status": RiskStatus.CRITICAL if shortfall > 0 else RiskStatus.NORMAL,
        "disclaimer": (
            "실제 연장근로시간 산정 기준(포괄임금 계약서상 가정 연장시간 vs "
            "실근무기록)에 따라 결과가 달라질 수 있으므로, 임금대장·근태기록과 "
            "대조해 확인이 필요합니다."
        ),
    }
