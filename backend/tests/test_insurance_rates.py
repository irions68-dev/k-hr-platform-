from datetime import date
from pathlib import Path

import pytest

from app.engines import insurance_rates

SAMPLE_RATE_YAML = """
effective_date: "{effective_date}"
national_pension:
  employee_rate: 0.045
  income_floor: 370000
  income_cap: 6370000
health_insurance:
  employee_rate: 0.03545
  long_term_care_rate: 0.1295
employment_insurance:
  employee_rate: 0.009
industrial_accident_insurance:
  rates_by_industry:
    제조업: 0.007
  default_rate: 0.01
non_taxable_allowances:
  meal_allowance_monthly_limit: 200000
  vehicle_allowance_monthly_limit: 200000
"""


@pytest.fixture()
def rates_dir(tmp_path: Path) -> Path:
    (tmp_path / "2025.yaml").write_text(
        SAMPLE_RATE_YAML.format(effective_date="2025-01-01"), encoding="utf-8"
    )
    (tmp_path / "2026.yaml").write_text(
        SAMPLE_RATE_YAML.format(effective_date="2026-01-01"), encoding="utf-8"
    )
    return tmp_path


def test_load_all_rate_tables_parses_every_file(rates_dir: Path):
    tables = insurance_rates.load_all_rate_tables(rates_dir)
    assert len(tables) == 2
    assert {t.effective_date for t in tables} == {date(2025, 1, 1), date(2026, 1, 1)}


def test_load_rates_for_date_picks_latest_applicable(rates_dir: Path):
    table = insurance_rates.load_rates_for_date(date(2026, 6, 1), rates_dir)
    assert table.effective_date == date(2026, 1, 1)


def test_load_rates_for_date_before_any_table_raises(rates_dir: Path):
    with pytest.raises(ValueError):
        insurance_rates.load_rates_for_date(date(2024, 1, 1), rates_dir)


def test_load_rates_for_date_between_years_picks_earlier(rates_dir: Path):
    table = insurance_rates.load_rates_for_date(date(2025, 6, 1), rates_dir)
    assert table.effective_date == date(2025, 1, 1)


def test_missing_directory_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        insurance_rates.load_all_rate_tables(tmp_path / "does-not-exist")
