"""
Machine model definition.
"""

from __future__ import annotations

from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, JSON

class Machine(SQLModel, table=True):
    """
    Model representing a laboratory machine.
    """
    id: Optional[str] = Field(default=None, primary_key=True, description="Unique identifier, e.g., 'CNC01'")
    name: str = Field(description="Name of the machine")
    sop: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Ordered list of standard operating procedure steps")
    safety_text: str = Field(description="Short safety instructions paragraph")
    emergency: bool = Field(default=False, description="Whether an emergency state is active")
    manual_text: str = Field(description="Full manual content describing operation, safety, and emergency shutdown")
