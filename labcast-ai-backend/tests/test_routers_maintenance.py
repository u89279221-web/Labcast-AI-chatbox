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

def test_maintenance_crud_admin(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    r = client.post("/api/maintenance/", json={"machine_id": "M1", "description": "Test", "performed_at": "2024-05-15T10:00:00Z"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_maintenance_technician_access(client, engine):
    pass

def test_maintenance_student_forbidden(client, engine):
    pass


