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
from unittest.mock import patch

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

def test_get_machine_config_success(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="student@labcast.edu", hashed_password=get_password_hash("123"), role="student")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "student@labcast.edu", "password": "123"})
    token = r.json()["access_token"]
    r = client.get("/api/machine/M1/config", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

@patch('app.routers.machine.publish_message')
def test_update_machine_success(mock_publish, client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    r = client.post("/api/machine/M1/update", json={"sop": ["new step"]}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    mock_publish.assert_called_once()

@patch('app.routers.machine.publish_message')
def test_emergency_state(mock_publish, client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    r = client.post("/api/machine/M1/emergency", json={"emergency": True}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    mock_publish.assert_called_once()


