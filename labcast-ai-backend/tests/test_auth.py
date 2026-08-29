import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.models.user import User
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

def test_login_success(client, engine):
    with Session(engine) as session:
        user = User(id="U1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        session.add(user)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_fail(client):
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "wrong"})
    assert r.status_code == 401

def test_rbac_admin_success(client, engine):
    with Session(engine) as session:
        user = User(id="U1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        session.add(user)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = client.post("/api/machine/M1/emergency", json={"emergency": True}, headers={"Authorization": f"Bearer {token}"})
    # Will fail 404 since M1 doesn't exist, but not 403
    assert r2.status_code == 404

def test_rbac_student_forbidden(client, engine):
    with Session(engine) as session:
        user = User(id="U2", email="student@labcast.edu", hashed_password=get_password_hash("student123"), role="student")
        session.add(user)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "student@labcast.edu", "password": "student123"})
    token = r.json()["access_token"]
    r2 = client.post("/api/machine/M1/emergency", json={"emergency": True}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403

def test_unauthenticated_fails(client):
    r = client.post("/api/machine/M1/emergency", json={"emergency": True})
    assert r.status_code == 401

def test_roles_list(client):
    r = client.get("/api/auth/roles")
    assert r.status_code == 200
    assert len(r.json()) == 4
    assert r.json()[0]["role"] == "admin"
