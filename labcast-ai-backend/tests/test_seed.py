import os
import pytest
from sqlmodel import create_engine, Session, SQLModel, select
from sqlalchemy.pool import StaticPool
from app.models.machine import Machine
from scripts.seed import seed_database

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

def test_seed_database(engine):
    seed_database(engine)
    with Session(engine) as session:
        machines = session.exec(select(Machine)).all()
        assert len(machines) == 3
        for m in machines:
            assert m.sop is not None
            assert m.safety_text is not None


