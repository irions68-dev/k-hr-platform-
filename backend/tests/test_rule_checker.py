from datetime import date, timedelta

from app.engines import rule_checker
from app.engines.rule_checker import DisguisedContractingFactors, RiskStatus


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
