from datetime import date, timedelta


def test_dispatch_worker_crud_and_risk(client):
    payload = {
        "name": "홍길동",
        "position": "생산직",
        "contract_start_date": (date.today() - timedelta(days=700)).isoformat(),
    }
    create_resp = client.post("/dispatch-workers", json=payload)
    assert create_resp.status_code == 200

    list_resp = client.get("/dispatch-workers")
    assert list_resp.status_code == 200
    workers = list_resp.json()
    assert len(workers) == 1
    assert workers[0]["d_day"] == 30
    assert workers[0]["status"] == "critical"


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


def test_morning_brief_aggregates_risk_and_study(client):
    client.post(
        "/dispatch-workers",
        json={
            "name": "김파견",
            "position": "사무직",
            "contract_start_date": (date.today() - timedelta(days=650)).isoformat(),
        },
    )
    client.post(
        "/dispatch-workers",
        json={
            "name": "이정상",
            "position": "사무직",
            "contract_start_date": date.today().isoformat(),
        },
    )
    client.post("/study/review-items", json={"keyword": "복습항목"})

    brief_resp = client.get("/brief/morning")
    assert brief_resp.status_code == 200
    brief = brief_resp.json()
    assert brief["total_workers"] == 2
    assert brief["at_risk_count"] == 1
    assert brief["at_risk_workers"][0]["name"] == "김파견"
    assert brief["due_study_count"] == 1


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
