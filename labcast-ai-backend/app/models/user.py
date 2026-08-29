from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """
    Model representing a user in the system.
    """
    id: str = Field(primary_key=True, description="Unique identifier (e.g. employee ID or email)")
    email: str = Field(unique=True, index=True, description="User's email address")
    hashed_password: str = Field(description="Bcrypt hashed password")
    role: str = Field(description="Role: admin, faculty, technician, or student")
