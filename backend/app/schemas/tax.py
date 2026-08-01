from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class FourInsurancesRequest(BaseModel):
    monthly_base_income: float = Field(gt=0)
    industry: str
    reference_date: date | None = None


class NonTaxableFilterRequest(BaseModel):
    gross_salary: float = Field(gt=0)
    meal_allowance: float = 0
    vehicle_allowance: float = 0
    reference_date: date | None = None
