from datetime import date, timedelta

from app.engines import rule_checker
from app.engines.rule_checker import (
    DisguisedContractingFactors,
    FreelancerMisclassificationFactors,
    RiskStatus,
)


def _limit_date(start: date) -> date:
    return start + timedelta(days=rule_checker.DISPATCH_LIMIT_DAYS)


class TestDispatchExpiration:
    def test_normal_when_far_from_limit(self):
        start = date(2025, 1, 1)
        reference = start + timedelta(days=1)
        result = rule_checker.check_dispatch_expiration(start, reference_date=reference)
        assert result["status"] == RiskStatus.NORMAL

    def test_warning_at_exactly_90_days(self):
        start = date(2025, 1, 1)
        reference = _limit_date(start) - timedelta(days=90)
        result = rule_checker.check_dispatch_expiration(start, reference_date=reference)
        assert result["d_day"] == 90
        assert result["status"] == RiskStatus.WARNING

    def test_normal_at_91_days(self):
        start = date(2025, 1, 1)
        reference = _limit_date(start) - timedelta(days=91)
        result = rule_checker.check_dispatch_expiration(start, reference_date=reference)
        assert result["status"] == RiskStatus.NORMAL

    def test_critical_at_exactly_30_days(self):
        start = date(2025, 1, 1)
        reference = _limit_date(start) - timedelta(days=30)
        result = rule_checker.check_dispatch_expiration(start, reference_date=reference)
        assert result["d_day"] == 30
        assert result["status"] == RiskStatus.CRITICAL

    def test_already_expired_is_critical(self):
        start = date(2020, 1, 1)
        reference = date(2025, 1, 1)
        result = rule_checker.check_dispatch_expiration(start, reference_date=reference)
        assert result["d_day"] < 0
        assert result["status"] == RiskStatus.CRITICAL


class TestWeeklyHourLimit:
    def test_within_limit(self):
        result = rule_checker.check_weekly_hour_limit(45)
        assert result["exceeded"] is False
        assert result["status"] == RiskStatus.NORMAL

    def test_exactly_at_limit_not_exceeded(self):
        result = rule_checker.check_weekly_hour_limit(52)
        assert result["exceeded"] is False

    def test_over_limit(self):
        result = rule_checker.check_weekly_hour_limit(55)
        assert result["exceeded"] is True
        assert result["excess_hours"] == 3
        assert result["status"] == RiskStatus.CRITICAL


class TestDisguisedContractingRisk:
    def test_no_risk_factors_is_normal(self):
        factors = DisguisedContractingFactors(False, False, False, False)
        result = rule_checker.assess_disguised_contracting_risk(factors)
        assert result["score"] == 0
        assert result["status"] == RiskStatus.NORMAL

    def test_one_risk_factor_is_warning(self):
        factors = DisguisedContractingFactors(True, False, False, False)
        result = rule_checker.assess_disguised_contracting_risk(factors)
        assert result["score"] == 1
        assert result["status"] == RiskStatus.WARNING

    def test_three_or_more_risk_factors_is_critical(self):
        factors = DisguisedContractingFactors(True, True, True, False)
        result = rule_checker.assess_disguised_contracting_risk(factors)
        assert result["score"] == 3
        assert result["status"] == RiskStatus.CRITICAL

    def test_response_always_includes_disclaimer(self):
        factors = DisguisedContractingFactors(False, False, False, False)
        result = rule_checker.assess_disguised_contracting_risk(factors)
        assert result["disclaimer"]


class TestSupervisoryIntermittentStatus:
    def test_no_approval_is_critical(self):
        result = rule_checker.check_supervisory_intermittent_status(False, None)
        assert result["status"] == RiskStatus.CRITICAL

    def test_valid_approval_is_normal(self):
        result = rule_checker.check_supervisory_intermittent_status(
            True, date(2030, 1, 1), reference_date=date(2026, 1, 1)
        )
        assert result["status"] == RiskStatus.NORMAL

    def test_expired_approval_is_critical(self):
        result = rule_checker.check_supervisory_intermittent_status(
            True, date(2020, 1, 1), reference_date=date(2026, 1, 1)
        )
        assert result["status"] == RiskStatus.CRITICAL


class TestMonthlyHourExemption:
    def test_below_threshold_is_exempt(self):
        result = rule_checker.check_monthly_hour_exemption(59)
        assert result["exempt_from_pension_and_health_insurance"] is True

    def test_at_threshold_is_not_exempt(self):
        result = rule_checker.check_monthly_hour_exemption(60)
        assert result["exempt_from_pension_and_health_insurance"] is False

    def test_above_threshold_is_not_exempt(self):
        result = rule_checker.check_monthly_hour_exemption(80)
        assert result["exempt_from_pension_and_health_insurance"] is False


class TestFreelancerMisclassificationRisk:
    def test_no_factors_is_normal(self):
        factors = FreelancerMisclassificationFactors(False, False, False, False)
        result = rule_checker.assess_freelancer_misclassification_risk(factors)
        assert result["score"] == 0
        assert result["status"] == RiskStatus.NORMAL

    def test_all_factors_is_critical(self):
        factors = FreelancerMisclassificationFactors(True, True, True, True)
        result = rule_checker.assess_freelancer_misclassification_risk(factors)
        assert result["score"] == 4
        assert result["status"] == RiskStatus.CRITICAL

    def test_response_always_includes_disclaimer(self):
        factors = FreelancerMisclassificationFactors(False, False, False, False)
        result = rule_checker.assess_freelancer_misclassification_risk(factors)
        assert result["disclaimer"]


class TestSeverancePay:
    def test_under_one_year_not_eligible(self):
        result = rule_checker.calculate_severance_pay(100000, tenure_days=300)
        assert result["eligible"] is False
        assert result["severance_pay"] == 0

    def test_exactly_one_year_is_eligible(self):
        result = rule_checker.calculate_severance_pay(100000, tenure_days=365)
        assert result["eligible"] is True
        assert result["severance_pay"] == round(100000 * 30 * (365 / 365))

    def test_two_years_calculates_proportionally(self):
        result = rule_checker.calculate_severance_pay(100000, tenure_days=730)
        assert result["severance_pay"] == round(100000 * 30 * (730 / 365))


class TestAnnualLeave:
    def test_under_one_year_accrues_monthly_capped_at_11(self):
        result = rule_checker.calculate_annual_leave(tenure_days=200)
        assert result["granted_days"] == 200 // 30

    def test_under_one_year_caps_at_11_days(self):
        result = rule_checker.calculate_annual_leave(tenure_days=364)
        assert result["granted_days"] <= 11

    def test_one_to_two_years_grants_15_days(self):
        result = rule_checker.calculate_annual_leave(tenure_days=400)
        assert result["granted_days"] == 15

    def test_three_years_grants_16_days(self):
        result = rule_checker.calculate_annual_leave(tenure_days=365 * 3)
        assert result["granted_days"] == 16

    def test_capped_at_25_days_for_long_tenure(self):
        result = rule_checker.calculate_annual_leave(tenure_days=365 * 30)
        assert result["granted_days"] == 25


class TestOvertimePremium:
    def test_overtime_only(self):
        result = rule_checker.calculate_overtime_premium(10000, overtime_hours=10)
        assert result["overtime_pay"] == round(10000 * 1.5 * 10)
        assert result["night_pay"] == 0
        assert result["holiday_pay"] == 0

    def test_holiday_hours_split_at_8(self):
        result = rule_checker.calculate_overtime_premium(10000, holiday_hours=10)
        expected = round(10000 * 1.5 * 8 + 10000 * 2.0 * 2)
        assert result["holiday_pay"] == expected

    def test_total_sums_all_components(self):
        result = rule_checker.calculate_overtime_premium(
            10000, overtime_hours=5, night_hours=3, holiday_hours=4
        )
        assert result["total_premium_pay"] == (
            result["overtime_pay"] + result["night_pay"] + result["holiday_pay"]
        )


class TestWeeklyHolidayPay:
    def test_below_15_hours_not_eligible(self):
        result = rule_checker.calculate_weekly_holiday_pay(14, 3, 10000)
        assert result["eligible"] is False
        assert result["pay"] == 0

    def test_not_full_attendance_not_eligible(self):
        result = rule_checker.calculate_weekly_holiday_pay(
            20, 4, 10000, full_attendance=False
        )
        assert result["eligible"] is False
        assert result["pay"] == 0

    def test_eligible_pays_daily_hours_times_wage(self):
        result = rule_checker.calculate_weekly_holiday_pay(20, 4, 10000)
        assert result["eligible"] is True
        assert result["pay"] == 40000

    def test_daily_hours_capped_at_8(self):
        result = rule_checker.calculate_weekly_holiday_pay(45, 9, 10000)
        assert result["pay"] == 80000


class TestComprehensiveWageAdequacy:
    def test_adequate_when_included_covers_required(self):
        required = round(10000 * 1.5 * 10)
        result = rule_checker.assess_comprehensive_wage_adequacy(
            required, actual_overtime_hours=10, hourly_wage=10000
        )
        assert result["adequate"] is True
        assert result["shortfall"] == 0
        assert result["status"] == RiskStatus.NORMAL

    def test_inadequate_when_included_is_less_than_required(self):
        result = rule_checker.assess_comprehensive_wage_adequacy(
            50000, actual_overtime_hours=10, hourly_wage=10000
        )
        required = round(10000 * 1.5 * 10)
        assert result["adequate"] is False
        assert result["shortfall"] == required - 50000
        assert result["status"] == RiskStatus.CRITICAL


class TestSupervisoryStatusNightPremiumNote:
    def test_note_present_regardless_of_approval(self):
        with_approval = rule_checker.check_supervisory_intermittent_status(True, None)
        without_approval = rule_checker.check_supervisory_intermittent_status(False, None)
        assert with_approval["night_premium_note"]
        assert without_approval["night_premium_note"]
