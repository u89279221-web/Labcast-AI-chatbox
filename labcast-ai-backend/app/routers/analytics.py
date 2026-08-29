from typing import List, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_session
from app.core.deps import RequireRole
from app.models.audit_log import AuditLog
from app.models.device import Device

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"]
)

class AnalyticsSummaryResponse(BaseModel):
    chats_per_machine: dict[str, int]
    total_emergency_activations: int
    active_devices: int

@router.get("/summary", response_model=AnalyticsSummaryResponse, dependencies=[Depends(RequireRole(["admin"]))])
def get_analytics_summary(session: Session = Depends(get_session)):
    """
    Get basic counts: chats per machine, emergency activations, active devices.
    """
    # 1. Chats per machine
    # Returns rows of (target_id, count)
    chats_query = select(AuditLog.target_id, func.count(AuditLog.id)).where(AuditLog.action == "chat").group_by(AuditLog.target_id)
    chats_result = session.exec(chats_query).all()
    chats_per_machine = {row[0]: row[1] for row in chats_result}

    # 2. Emergency activations count
    emergency_query = select(func.count(AuditLog.id)).where(AuditLog.action == "emergency_toggle")
    total_emergency_activations = session.exec(emergency_query).one_or_none() or 0

    # 3. Active devices count
    active_devices_query = select(func.count(Device.id)).where(Device.status == "online")
    active_devices = session.exec(active_devices_query).one_or_none() or 0

    return AnalyticsSummaryResponse(
        chats_per_machine=chats_per_machine,
        total_emergency_activations=total_emergency_activations,
        active_devices=active_devices
    )

@router.get("/logs", response_model=List[AuditLog], dependencies=[Depends(RequireRole(["admin"]))])
def get_audit_logs(limit: int = 50, session: Session = Depends(get_session)):
    """
    Get recent audit logs.
    """
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    return session.exec(query).all()
