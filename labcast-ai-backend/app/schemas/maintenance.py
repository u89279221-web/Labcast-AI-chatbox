from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MaintenanceCreate(BaseModel):
    machine_id: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    performed_at: datetime
    next_due_at: Optional[datetime] = None

class MaintenanceUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    performed_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None

class MaintenanceResponse(BaseModel):
    id: str
    machine_id: str
    technician_id: str
    description: str
    performed_at: datetime
    next_due_at: Optional[datetime] = None
