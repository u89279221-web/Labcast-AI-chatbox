import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_session
from app.models.user import User
from app.core.security import get_password_hash
from app.models.machine import Machine

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

def test_register_device(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    r = client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_device_heartbeat(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    
    r = client.post("/api/device/D1/heartbeat", json={"config_version": "1.0", "wifi_signal": -60}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

def test_send_device_test_message(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    
    r = client.post("/api/device/D1/test-message", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"

def test_restart_device(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    
    r = client.post("/api/device/D1/restart", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"

def test_list_firmware_templates(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        session.add(user)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    
    r = client.get("/api/device/firmware/templates", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) > 0
    assert r.json()[0]["id"] == "basic"

def test_trigger_ota_update(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    
    r = client.post("/api/device/D1/ota", json={"template_id": "basic"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"

def test_revoke_device(client, engine):
    with Session(engine) as session:
        user = User(id="A1", email="admin@labcast.edu", hashed_password=get_password_hash("admin123"), role="admin")
        m = Machine(id="M1", name="Test", safety_text="Safe", sop=["step"], manual_text="")
        session.add(user)
        session.add(m)
        session.commit()
    r = client.post("/api/auth/login", data={"username": "admin@labcast.edu", "password": "admin123"})
    token = r.json()["access_token"]
    client.post("/api/device/register", json={"id": "D1", "machine_id": "M1", "firmware_version": "1.0"}, headers={"Authorization": f"Bearer {token}"})
    
    r = client.delete("/api/device/D1", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"


