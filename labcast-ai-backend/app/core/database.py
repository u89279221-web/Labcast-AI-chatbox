"""
Database configuration and session management.
Uses SQLite for the initial stage.
"""

from collections.abc import Generator
from sqlmodel import Session, create_engine

from app.core.config import settings

# Create database engine
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False, # Disable echo in production, can enable for local debug if needed
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Database and table creation is now managed via Alembic. 
    This function remains as a placeholder/no-op for lifespan events 
    so the app doesn't try to recreate tables on every startup.
    """
    pass
