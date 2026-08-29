import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_session

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

def test_login_rate_limiting(client):
    for _ in range(10):
        client.post("/api/auth/login", data={"username": "a@b.com", "password": "123"})
    r = client.post("/api/auth/login", data={"username": "a@b.com", "password": "123"})
    assert r.status_code == 429

