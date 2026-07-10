import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.mock_provider import MockAIProvider
from app.ai.provider import get_ai_provider
from app.db.session import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    from app.core.rate_limit import _memory_windows

    _memory_windows.clear()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    # Seed badges + one coding problem
    from app.models import Badge, CodingProblem
    from app.services.gamification_service import BADGE_DEFS
    import json

    with TestSession() as db:
        for code, name, description, icon in BADGE_DEFS:
            db.add(Badge(code=code, name=name, description=description, icon=icon))
        db.add(
            CodingProblem(
                title="Echo Sum",
                slug="echo-sum",
                description="Read two ints on one line, print their sum.",
                difficulty="easy",
                topic="math",
                starter_code_json=json.dumps({"python": ""}),
                visible_tests_json=json.dumps([{"input": "1 2", "expected": "3"}]),
                hidden_tests_json=json.dumps([{"input": "10 -4", "expected": "6"}]),
            )
        )
        db.commit()

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "t@t.com", "password": "Passw0rd1", "full_name": "Tester"},
    )
    tokens = client.post(
        "/api/v1/auth/login", json={"email": "t@t.com", "password": "Passw0rd1"}
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
