from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
import uuid

def get_utc_now():
    from datetime import timezone
    return datetime.now(timezone.utc)

class AuditLog(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[str] = Field(default=None, description="ID of the user who performed the action, if known")
    action: str = Field(description="The action performed, e.g., 'machine_update', 'emergency_toggle', 'chat'")
    target_type: str = Field(description="The type of the target, e.g., 'machine', 'document', 'user'")
    target_id: str = Field(description="The ID of the target being affected")
    timestamp: datetime = Field(default_factory=get_utc_now, description="When the action occurred")
    details: Optional[str] = Field(default=None, description="JSON string or text with additional context")
