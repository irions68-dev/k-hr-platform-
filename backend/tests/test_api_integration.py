from datetime import date, timedelta


def test_case_note_create_and_search(client):
    payload = {
        "question": "위장도급 판단기준이 뭐야?",
        "answer": "고용노동부 4대 판단기준을 참고해야 합니다.",
        "legal_references": ["파견법 제6조"],
        "exam_part": "노동법 제2부",
        "core_keyword": "위장도급",
        "importance": "High",
    }
    create_resp = client.post("/cases", json=payload)
    assert create_resp.status_code == 200

    search_resp = client.get("/cases/search", params={"q": "위장도급"})
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) == 1
    assert results[0]["legal_references"] == ["파견법 제6조"]

    no_match_resp = client.get("/cases/search", params={"q": "존재하지않는키워드"})
    assert no_match_resp.json() == []


def test_study_review_flow(client):
    item_resp = client.post("/study/review-items", json={"keyword": "위장도급 판단기준"})
    assert item_resp.status_code == 200
    item_id = item_resp.json()["id"]

    due_resp = client.get("/study/due")
    assert due_resp.status_code == 200
    assert any(item["id"] == item_id for item in due_resp.json())

    review_resp = client.post(
        f"/study/review-items/{item_id}/review", json={"quality": 5}
    )
    assert review_resp.status_code == 200
    updated = review_resp.json()
    assert updated["repetitions"] == 1
    assert updated["interval_days"] == 1

    missing_resp = client.post("/study/review-items/9999/review", json={"quality": 5})
    assert missing_resp.status_code == 404


def test_morning_brief_aggregates_due_study_items(client):
    client.post("/study/review-items", json={"keyword": "복습항목"})

    brief_resp = client.get("/brief/morning")
    assert brief_resp.status_code == 200
    brief = brief_resp.json()
    assert brief["due_study_count"] == 1
    assert brief["due_study_items"][0]["keyword"] == "복습항목"


def test_dispatch_expiration_calculator_is_stateless(client):
    contract_start = date.today() - timedelta(days=700)
    resp = client.post(
        "/risk/dispatch-expiration",
        json={"contract_start_date": contract_start.isoformat()},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["d_day"] == 30
    assert body["status"] == "critical"


def test_severance_pay_calculator(client):
    hire_date = date.today() - timedelta(days=730)
    resp = client.post(
        "/calculators/severance-pay",
        json={"hire_date": hire_date.isoformat(), "average_daily_wage": 100000},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["eligible"] is True
    assert body["severance_pay"] > 0


def test_annual_leave_calculator(client):
    hire_date = date.today() - timedelta(days=400)
    resp = client.post(
        "/calculators/annual-leave", json={"hire_date": hire_date.isoformat()}
    )
    assert resp.status_code == 200
    assert resp.json()["granted_days"] == 15


def test_overtime_premium_calculator(client):
    resp = client.post(
        "/calculators/overtime-premium",
        json={"hourly_wage": 10000, "overtime_hours": 5},
    )
    assert resp.status_code == 200
    assert resp.json()["overtime_pay"] == round(10000 * 1.5 * 5)


def test_four_insurances_endpoint(client):
    resp = client.post(
        "/tax/four-insurances",
        json={"monthly_base_income": 3000000, "industry": "제조업"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["national_pension"]["premium"] > 0
    assert body["industrial_accident_insurance"]["industry"] == "제조업"
    assert body["employee_total_premium"] == (
        body["national_pension"]["premium"]
        + body["health_insurance"]["total_premium"]
        + body["employment_insurance"]["premium"]
    )


def test_non_taxable_filter_endpoint(client):
    resp = client.post(
        "/tax/non-taxable-filter",
        json={
            "gross_salary": 3000000,
            "meal_allowance": 300000,
            "vehicle_allowance": 100000,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["non_taxable_meal"] == 200000  # 20만원 한도 초과분은 컷
    assert body["non_taxable_vehicle"] == 100000
    assert body["taxable_base_income"] == 3000000 - 300000
