import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import AUTH_HEADER
from app.core.db import Base, get_db
from app.main import app


@pytest.fixture()
def authed_client(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "secret123")

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_request_without_password_is_rejected(authed_client):
    resp = authed_client.get("/study/due")
    assert resp.status_code == 401


def test_401_response_still_carries_cors_headers(authed_client):
    # 미들웨어 순서가 뒤바뀌면 401 응답에 CORS 헤더가 빠져서 브라우저가
    # net::ERR_FAILED로 처리해버린다(실제 겪은 회귀) - 순서 고정용 테스트.
    resp = authed_client.get(
        "/study/due", headers={"Origin": "http://localhost:3010"}
    )
    assert resp.status_code == 401
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3010"


def test_request_with_wrong_password_is_rejected(authed_client):
    resp = authed_client.get("/study/due", headers={AUTH_HEADER: "wrong"})
    assert resp.status_code == 401


def test_request_with_correct_password_succeeds(authed_client):
    resp = authed_client.get("/study/due", headers={AUTH_HEADER: "secret123"})
    assert resp.status_code == 200


def test_health_endpoint_is_exempt(authed_client):
    resp = authed_client.get("/health")
    assert resp.status_code == 200


def test_auth_disabled_when_no_password_set(client):
    # conftest.py의 client fixture는 APP_PASSWORD를 설정하지 않음
    resp = client.get("/study/due")
    assert resp.status_code == 200
