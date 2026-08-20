from app.engines import (
    assistant_router,
    attrition_signal,
    complaint_defense,
    compliance_check,
    message_draft,
)


def test_route_dispatches_to_complaint_defense(monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "generate_structured_json",
        lambda *a, **kw: {"category": "complaint_defense"},
    )
    monkeypatch.setattr(
        complaint_defense,
        "generate_defense",
        lambda text: {
            "defense_response": "답변",
            "legal_basis": [],
            "legal_basis_explanation": "설명",
            "caution_note": "유의",
        },
    )

    result = assistant_router.route("무단결근인데 왜 월차 차감하냐고 항의하는 카톡")

    assert result["category"] == "complaint_defense"
    assert result["category_label"] == "민원 방어"
    assert result["result"]["defense_response"] == "답변"


def test_route_dispatches_to_compliance_check(monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "generate_structured_json",
        lambda *a, **kw: {"category": "compliance_check"},
    )
    monkeypatch.setattr(
        compliance_check,
        "check_compliance",
        lambda text: {
            "risk_level": "높음",
            "risk_summary": "요약",
            "legal_references": [],
            "pitch": "피치",
        },
    )

    result = assistant_router.route("3년째 같은 인력을 파견 형태로 사용 중")

    assert result["category"] == "compliance_check"
    assert result["result"]["risk_level"] == "높음"


def test_route_dispatches_to_attrition_signal(monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "generate_structured_json",
        lambda *a, **kw: {"category": "attrition_signal"},
    )
    monkeypatch.setattr(
        attrition_signal,
        "analyze_signals",
        lambda text: {
            "observed_signals": ["답장이 늦어짐"],
            "suggested_approach": "제안",
            "talking_points": ["포인트"],
            "caution_note": "유의",
        },
    )

    result = assistant_router.route("요즘 답장이 늦어졌어요")

    assert result["category"] == "attrition_signal"
    assert result["result"]["observed_signals"] == ["답장이 늦어짐"]


def test_route_dispatches_to_message_draft(monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "generate_structured_json",
        lambda *a, **kw: {"category": "message_draft"},
    )
    monkeypatch.setattr(
        message_draft,
        "generate_drafts",
        lambda text: {
            "client_email": "이메일",
            "worker_message": "메시지",
            "interviewer_memo": "메모",
        },
    )

    result = assistant_router.route("면접 일정 안내, 대상자 3명, 내일 오후 2시")

    assert result["category"] == "message_draft"
    assert result["result"]["client_email"] == "이메일"


def test_route_falls_back_to_message_draft_for_unknown_category(monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "generate_structured_json",
        lambda *a, **kw: {"category": "존재하지않는카테고리"},
    )
    monkeypatch.setattr(
        message_draft,
        "generate_drafts",
        lambda text: {
            "client_email": "이메일",
            "worker_message": "메시지",
            "interviewer_memo": "메모",
        },
    )

    result = assistant_router.route("애매한 텍스트")

    assert result["category"] == "message_draft"


def test_assistant_router_api_round_trip(client, monkeypatch):
    monkeypatch.setattr(
        assistant_router,
        "route",
        lambda text: {
            "category": "complaint_defense",
            "category_label": "민원 방어",
            "result": {"defense_response": "답변"},
        },
    )

    resp = client.post("/assistant/route", json={"text": "아무 텍스트"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "complaint_defense"
    assert body["result"]["defense_response"] == "답변"


def test_assistant_router_api_rejects_empty_text(client):
    resp = client.post("/assistant/route", json={"text": ""})
    assert resp.status_code == 422
