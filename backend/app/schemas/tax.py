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


class ProratedInsuranceRequest(BaseModel):
    monthly_base_income: float = Field(gt=0)
    industry: str
    days_worked: int = Field(gt=0)
    days_in_month: int = Field(gt=0, le=31)
    reference_date: date | None = None
