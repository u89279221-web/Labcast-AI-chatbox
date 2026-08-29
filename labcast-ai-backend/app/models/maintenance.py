from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class MaintenanceRecord(SQLModel, table=True):
    """
    Model representing a maintenance action on a machine.
    """
    id: Optional[str] = Field(default=None, primary_key=True, description="Unique identifier for the record")
    machine_id: str = Field(foreign_key="machine.id", description="The machine being maintained")
    technician_id: str = Field(foreign_key="user.id", description="The technician who performed the maintenance")
    description: str = Field(description="Description of the maintenance performed")
    performed_at: datetime = Field(description="When the maintenance was performed (UTC)")
    next_due_at: Optional[datetime] = Field(default=None, description="When the next maintenance is due (UTC)")
