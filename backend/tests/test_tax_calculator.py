from app.engines.insurance_rates import (
    EmploymentInsuranceRates,
    HealthInsuranceRates,
    IndustrialAccidentRates,
    NationalPensionRates,
    NonTaxableLimits,
)
from app.engines.tax_calculator import (
    AllowanceInput,
    calculate_employment_insurance,
    calculate_health_insurance,
    calculate_industrial_accident_insurance,
    calculate_national_pension,
    filter_non_taxable_allowances,
)

PENSION_RATES = NationalPensionRates(
    employee_rate=0.045, income_floor=370000, income_cap=6370000
)
HEALTH_RATES = HealthInsuranceRates(employee_rate=0.03545, long_term_care_rate=0.1295)
EMPLOYMENT_RATES = EmploymentInsuranceRates(employee_rate=0.009)
INDUSTRIAL_RATES = IndustrialAccidentRates(
    rates_by_industry={"제조업": 0.007, "건설업": 0.036}, default_rate=0.01
)
NON_TAXABLE_LIMITS = NonTaxableLimits(
    meal_allowance_monthly_limit=200000, vehicle_allowance_monthly_limit=200000
)


class TestNationalPension:
    def test_within_range_uses_actual_income(self):
        result = calculate_national_pension(3000000, PENSION_RATES)
        assert result["base_income"] == 3000000
        assert result["premium"] == round(3000000 * 0.045)

    def test_below_floor_uses_floor(self):
        result = calculate_national_pension(100000, PENSION_RATES)
        assert result["base_income"] == 370000

    def test_above_cap_uses_cap(self):
        result = calculate_national_pension(10000000, PENSION_RATES)
        assert result["base_income"] == 6370000
        assert result["premium"] == round(6370000 * 0.045)


class TestHealthInsurance:
    def test_includes_long_term_care_premium(self):
        result = calculate_health_insurance(3000000, HEALTH_RATES)
        expected_health = round(3000000 * 0.03545)
        expected_ltc = round(expected_health * 0.1295)
        assert result["health_premium"] == expected_health
        assert result["long_term_care_premium"] == expected_ltc
        assert result["total_premium"] == expected_health + expected_ltc


class TestEmploymentInsurance:
    def test_premium_calculation(self):
        result = calculate_employment_insurance(3000000, EMPLOYMENT_RATES)
        assert result["premium"] == round(3000000 * 0.009)


class TestIndustrialAccidentInsurance:
    def test_known_industry_uses_specific_rate(self):
        result = calculate_industrial_accident_insurance(3000000, "건설업", INDUSTRIAL_RATES)
        assert result["rate"] == 0.036
        assert result["employer_only"] is True

    def test_unknown_industry_falls_back_to_default(self):
        result = calculate_industrial_accident_insurance(3000000, "IT업", INDUSTRIAL_RATES)
        assert result["rate"] == 0.01


class TestNonTaxableAllowances:
    def test_allowances_within_limit_fully_excluded(self):
        allowances = AllowanceInput(meal_allowance=150000, vehicle_allowance=100000)
        result = filter_non_taxable_allowances(3000000, allowances, NON_TAXABLE_LIMITS)
        assert result["non_taxable_meal"] == 150000
        assert result["non_taxable_vehicle"] == 100000
        assert result["taxable_base_income"] == 3000000 - 250000

    def test_allowances_over_limit_are_capped(self):
        allowances = AllowanceInput(meal_allowance=300000, vehicle_allowance=250000)
        result = filter_non_taxable_allowances(3000000, allowances, NON_TAXABLE_LIMITS)
        assert result["non_taxable_meal"] == 200000
        assert result["non_taxable_vehicle"] == 200000
        assert result["total_non_taxable"] == 400000
