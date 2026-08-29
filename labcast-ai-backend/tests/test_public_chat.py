import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.models.user import User
from app.models.machine import Machine
from app.core.security import get_password_hash

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:"),
        connect_args={"check_same_thread": False} if "sqlite" in os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:") else {},
        poolclass=StaticPool if "sqlite" in os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:") else None
    )
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    from app.main import limiter
    limiter._storage.reset()
    yield client
    app.dependency_overrides.clear()

def test_unauthenticated_chat_and_config_succeeds(client, engine):
    with Session(engine) as session:
        # Seed a machine
        m = Machine(id="M_TEST", name="Test Machine", safety_text="Wear Goggles", sop=["Step 1"], manual_text="Context info")
        session.add(m)
        session.commit()

    # 1. GET /config without auth token should succeed
    r_config = client.get("/api/machine/M_TEST/config")
    assert r_config.status_code == 200
    assert r_config.json()["name"] == "Test Machine"

    # 2. POST /chat without auth token should succeed
    r_chat = client.post("/api/machine/M_TEST/chat", json={"question": "What is the safety instruction?"})
    assert r_chat.status_code == 200
    assert "answer" in r_chat.json()

def test_unauthenticated_protected_endpoint_returns_401(client, engine):
    with Session(engine) as session:
        m = Machine(id="M_TEST", name="Test Machine", safety_text="Wear Goggles", sop=["Step 1"], manual_text="")
        session.add(m)
        session.commit()

    # Call a protected machine update endpoint without auth token
    r_update = client.post("/api/machine/M_TEST/update", json={"safety_text": "Updated safety"})
    assert r_update.status_code == 401

def test_unauthenticated_chat_rate_limiting(client, engine):
    with Session(engine) as session:
        m = Machine(id="M_TEST", name="Test Machine", safety_text="Wear Goggles", sop=["Step 1"], manual_text="Context info")
        session.add(m)
        session.commit()

    # Unauthenticated guest: dynamic limit provider should limit to 5/minute
    # Make 5 requests successfully
    for _ in range(5):
        r = client.post("/api/machine/M_TEST/chat", json={"question": "hello"})
        assert r.status_code == 200

    # The 6th request should fail with 429 Too Many Requests
    r_limit = client.post("/api/machine/M_TEST/chat", json={"question": "hello"})
    assert r_limit.status_code == 429

def test_authenticated_chat_higher_rate_limit(client, engine):
    with Session(engine) as session:
        # Seed user and machine
        user = User(id="S1", email="student@labcast.edu", hashed_password=get_password_hash("pwd123"), role="student")
        m = Machine(id="M_TEST", name="Test Machine", safety_text="Wear Goggles", sop=["Step 1"], manual_text="Context info")
        session.add(user)
        session.add(m)
        session.commit()

    # Login to get token
    r_login = client.post("/api/auth/login", data={"username": "student@labcast.edu", "password": "pwd123"})
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Make 8 requests (which is more than the public limit of 5, but allowed under the authenticated limit of 60)
    for _ in range(8):
        r = client.post("/api/machine/M_TEST/chat", json={"question": "hello"}, headers=headers)
        assert r.status_code == 200
