"""4대보험 및 비과세 수당 계산 로직.

요율 수치 자체는 이 파일에 두지 않고 `insurance_rates.InsuranceRateTable`을
인자로 받는다 - 요율이 바뀌어도 이 파일은 건드릴 필요가 없어야 한다.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engines.insurance_rates import (
    EmploymentInsuranceRates,
    HealthInsuranceRates,
    IndustrialAccidentRates,
    InsuranceRateTable,
    NationalPensionRates,
    NonTaxableLimits,
)


def calculate_national_pension(
    monthly_base_income: float, rates: NationalPensionRates
) -> dict:
    """국민연금 기준소득월액은 상·하한액 범위로 조정된 뒤 요율이 적용된다."""
    capped_income = min(max(monthly_base_income, rates.income_floor), rates.income_cap)
    premium = round(capped_income * rates.employee_rate)
    return {
        "base_income": capped_income,
        "employee_rate": rates.employee_rate,
        "premium": premium,
    }


def calculate_health_insurance(
    monthly_base_income: float, rates: HealthInsuranceRates
) -> dict:
    """건강보험료 + 장기요양보험료(건강보험료 대비 비율)."""
    health_premium = round(monthly_base_income * rates.employee_rate)
    long_term_care_premium = round(health_premium * rates.long_term_care_rate)
    return {
        "health_premium": health_premium,
        "long_term_care_premium": long_term_care_premium,
        "total_premium": health_premium + long_term_care_premium,
    }


def calculate_employment_insurance(
    monthly_base_income: float, rates: EmploymentInsuranceRates
) -> dict:
    """고용보험료 중 근로자 부담분(실업급여 계정)."""
    premium = round(monthly_base_income * rates.employee_rate)
    return {"premium": premium}


def calculate_industrial_accident_insurance(
    monthly_base_income: float, industry: str, rates: IndustrialAccidentRates
) -> dict:
    """산재보험료는 전액 사업주 부담이지만, 예산 산정 참고용으로 계산해서 제공한다."""
    rate = rates.rates_by_industry.get(industry, rates.default_rate)
    premium = round(monthly_base_income * rate)
    return {
        "industry": industry,
        "rate": rate,
        "premium": premium,
        "employer_only": True,
    }


def calculate_four_insurances(
    monthly_base_income: float, industry: str, rate_table: InsuranceRateTable
) -> dict:
    pension = calculate_national_pension(monthly_base_income, rate_table.national_pension)
    health = calculate_health_insurance(monthly_base_income, rate_table.health_insurance)
    employment = calculate_employment_insurance(
        monthly_base_income, rate_table.employment_insurance
    )
    industrial = calculate_industrial_accident_insurance(
        monthly_base_income, industry, rate_table.industrial_accident
    )

    employee_total_premium = (
        pension["premium"] + health["total_premium"] + employment["premium"]
    )

    return {
        "rate_effective_date": rate_table.effective_date,
        "national_pension": pension,
        "health_insurance": health,
        "employment_insurance": employment,
        "industrial_accident_insurance": industrial,
        "employee_total_premium": employee_total_premium,
    }


def calculate_prorated_four_insurances(
    monthly_base_income: float,
    industry: str,
    days_worked: int,
    days_in_month: int,
    rate_table: InsuranceRateTable,
) -> dict:
    """월 중도 입사·퇴사 시 보험료를 근무일수 비례로 일할계산한다(근사치).

    주의: 실제로는 국민연금·건강보험은 원칙적으로 월 단위 부과이고 일할계산을
    적용하지 않는 경우가 많으며, 보험 종류별로 취득/상실 시점 처리 규정이
    다르다. 이 함수는 전화 응대 시 즉시 답할 수 있는 근사치를 제공할 뿐이며,
    정확한 금액은 4대사회보험 정보연계센터 확인이 필요하다.
    """
    full = calculate_four_insurances(monthly_base_income, industry, rate_table)
    ratio = days_worked / days_in_month

    def scale(amount: int) -> int:
        return round(amount * ratio)

    return {
        "days_worked": days_worked,
        "days_in_month": days_in_month,
        "proration_ratio": round(ratio, 4),
        "national_pension_premium": scale(full["national_pension"]["premium"]),
        "health_insurance_premium": scale(full["health_insurance"]["total_premium"]),
        "employment_insurance_premium": scale(full["employment_insurance"]["premium"]),
        "employee_total_premium": scale(full["employee_total_premium"]),
        "disclaimer": (
            "근무일수 비례 근사치입니다. 국민연금·건강보험은 실제로 월 단위 "
            "부과 원칙이 적용되는 경우가 많으므로, 정확한 금액은 공단 확인이 "
            "필요합니다."
        ),
    }


@dataclass
class AllowanceInput:
    meal_allowance: float = 0
    vehicle_allowance: float = 0


def filter_non_taxable_allowances(
    gross_salary: float, allowances: AllowanceInput, limits: NonTaxableLimits
) -> dict:
    """비과세 수당(식대·자가운전보조금 등)을 한도 내에서 걸러내 과세표준을 산출한다."""
    non_taxable_meal = min(allowances.meal_allowance, limits.meal_allowance_monthly_limit)
    non_taxable_vehicle = min(
        allowances.vehicle_allowance, limits.vehicle_allowance_monthly_limit
    )
    total_non_taxable = non_taxable_meal + non_taxable_vehicle

    return {
        "non_taxable_meal": non_taxable_meal,
        "non_taxable_vehicle": non_taxable_vehicle,
        "total_non_taxable": total_non_taxable,
        "taxable_base_income": gross_salary - total_non_taxable,
    }
