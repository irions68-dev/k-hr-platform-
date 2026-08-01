"""4대보험 요율 설정 로더.

요율은 매년(때로는 연중에도) 개정되므로 코드에 하드코딩하지 않고
`app/config/insurance_rates/*.yaml` 파일에서 적용일자 기준으로 조회한다.
요율이 바뀌면 새 연도 파일만 추가하면 되고 코드 배포는 필요 없다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

RATES_DIR = Path(__file__).resolve().parent.parent / "config" / "insurance_rates"


@dataclass
class NationalPensionRates:
    employee_rate: float
    income_floor: float
    income_cap: float


@dataclass
class HealthInsuranceRates:
    employee_rate: float
    long_term_care_rate: float  # 건강보험료 대비 장기요양보험료 비율


@dataclass
class EmploymentInsuranceRates:
    employee_rate: float


@dataclass
class IndustrialAccidentRates:
    rates_by_industry: dict[str, float]
    default_rate: float


@dataclass
class NonTaxableLimits:
    meal_allowance_monthly_limit: float
    vehicle_allowance_monthly_limit: float


@dataclass
class InsuranceRateTable:
    effective_date: date
    national_pension: NationalPensionRates
    health_insurance: HealthInsuranceRates
    employment_insurance: EmploymentInsuranceRates
    industrial_accident: IndustrialAccidentRates
    non_taxable: NonTaxableLimits


def _parse_rate_file(path: Path) -> InsuranceRateTable:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return InsuranceRateTable(
        effective_date=date.fromisoformat(str(data["effective_date"])),
        national_pension=NationalPensionRates(**data["national_pension"]),
        health_insurance=HealthInsuranceRates(**data["health_insurance"]),
        employment_insurance=EmploymentInsuranceRates(**data["employment_insurance"]),
        industrial_accident=IndustrialAccidentRates(
            rates_by_industry=data["industrial_accident_insurance"]["rates_by_industry"],
            default_rate=data["industrial_accident_insurance"]["default_rate"],
        ),
        non_taxable=NonTaxableLimits(**data["non_taxable_allowances"]),
    )


def load_all_rate_tables(rates_dir: Path | None = None) -> list[InsuranceRateTable]:
    directory = rates_dir or RATES_DIR
    if not directory.exists():
        raise FileNotFoundError(f"요율 설정 디렉토리를 찾을 수 없습니다: {directory}")

    tables = [_parse_rate_file(p) for p in sorted(directory.glob("*.yaml"))]
    if not tables:
        raise FileNotFoundError(f"요율 설정 파일이 없습니다: {directory}")
    return tables


def load_rates_for_date(
    effective_date: date, rates_dir: Path | None = None
) -> InsuranceRateTable:
    """주어진 날짜에 적용되는 요율 테이블을 조회한다.

    effective_date가 조회일 이전(또는 같은 날)인 테이블 중 가장 최신 것을 선택한다.
    """
    tables = load_all_rate_tables(rates_dir)
    applicable = [t for t in tables if t.effective_date <= effective_date]
    if not applicable:
        raise ValueError(f"{effective_date} 이전에 적용 가능한 요율 테이블이 없습니다.")
    return max(applicable, key=lambda t: t.effective_date)
