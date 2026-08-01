from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from app.engines import insurance_rates, tax_calculator
from app.schemas.tax import FourInsurancesRequest, NonTaxableFilterRequest

router = APIRouter(prefix="/tax", tags=["tax"])


@router.post("/four-insurances")
def four_insurances(payload: FourInsurancesRequest) -> dict:
    reference_date = payload.reference_date or date.today()
    rate_table = insurance_rates.load_rates_for_date(reference_date)
    return tax_calculator.calculate_four_insurances(
        payload.monthly_base_income, payload.industry, rate_table
    )


@router.post("/non-taxable-filter")
def non_taxable_filter(payload: NonTaxableFilterRequest) -> dict:
    reference_date = payload.reference_date or date.today()
    rate_table = insurance_rates.load_rates_for_date(reference_date)
    allowances = tax_calculator.AllowanceInput(
        meal_allowance=payload.meal_allowance,
        vehicle_allowance=payload.vehicle_allowance,
    )
    return tax_calculator.filter_non_taxable_allowances(
        payload.gross_salary, allowances, rate_table.non_taxable
    )
