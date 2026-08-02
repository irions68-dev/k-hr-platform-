import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.main import app


@pytest.fixture()
def client(monkeypatch):
    # lifespan이 부팅 시 샘플 코퍼스를 자동 적재하는데(app/main.py), 이 앱을
    # 그냥 띄우기만 하는 테스트에서까지 실제 Gemini 임베딩 API를 부르면 느리고
    # 쿼터도 낭비된다. 키를 지워서 조용히 스킵되게 한다(main.py가 실패를
    # 삼키도록 이미 처리돼 있음).
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
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
