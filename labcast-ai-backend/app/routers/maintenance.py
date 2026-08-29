import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import logging

from app.core.database import get_session
from app.core.deps import get_current_user, RequireRole
from app.models.maintenance import MaintenanceRecord
from app.models.machine import Machine
from app.models.user import User
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse
from app.core.audit import log_action

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[MaintenanceResponse], dependencies=[Depends(RequireRole(["admin", "technician"]))])
def list_maintenance_records(machine_id: Optional[str] = None, session: Session = Depends(get_session)):
    """List maintenance records. Optionally filter by machine_id."""
    query = select(MaintenanceRecord)
    if machine_id:
        query = query.where(MaintenanceRecord.machine_id == machine_id)
    records = session.exec(query).all()
    return records

@router.post("/", response_model=MaintenanceResponse, dependencies=[Depends(RequireRole(["admin", "technician"]))])
def create_maintenance_record(req: MaintenanceCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Create a new maintenance record."""
    machine = session.get(Machine, req.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
        
    record_id = str(uuid.uuid4())
    record = MaintenanceRecord(
        id=record_id,
        machine_id=req.machine_id,
        technician_id=current_user.id,
        description=req.description,
        performed_at=req.performed_at,
        next_due_at=req.next_due_at
    )
    
    session.add(record)
    session.commit()
    session.refresh(record)
    logger.info(f"Maintenance record {record_id} created for machine {req.machine_id} by {current_user.id}")
    
    log_action(session, "create_maintenance", "maintenance_record", record_id, current_user.id, {"machine_id": req.machine_id})
    
    return record

@router.put("/{record_id}", response_model=MaintenanceResponse, dependencies=[Depends(RequireRole(["admin", "technician"]))])
def update_maintenance_record(record_id: str, req: MaintenanceUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Update an existing maintenance record."""
    record = session.get(MaintenanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found.")
        
    if req.description is not None:
        record.description = req.description
    if req.performed_at is not None:
        record.performed_at = req.performed_at
    if req.next_due_at is not None:
        record.next_due_at = req.next_due_at
        
    session.add(record)
    session.commit()
    session.refresh(record)
    
    log_action(session, "update_maintenance", "maintenance_record", record_id, current_user.id, {"machine_id": record.machine_id})
    
    return record
