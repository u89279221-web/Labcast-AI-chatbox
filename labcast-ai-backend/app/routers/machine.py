"""
API router for Machine endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import get_current_user, RequireRole, get_optional_user
from app.models.machine import Machine
from app.schemas.machine import MachineConfigResponse, MachineUpdateRequest, EmergencyRequest, ChatRequest, ChatResponse
from app.chatbot.chat import process_chat_query
from app.mqtt.publisher import publish_message
from app.core.audit import log_action
from app.models.user import User
from app.core.limiter import limiter, request_var

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/machine",
    tags=["machine"]
)

@router.get("/", response_model=list[Machine])
def list_machines(session: Session = Depends(get_session)):
    """
    List all machines.
    """
    return session.exec(select(Machine)).all()

@router.get("/{machine_id}/config", response_model=MachineConfigResponse)
def get_machine_config(machine_id: str, session: Session = Depends(get_session)):
    """
    Get the configuration for a specific machine.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    return machine

@router.post("/{machine_id}/update", response_model=MachineConfigResponse, dependencies=[Depends(RequireRole(["admin", "faculty"]))])
def update_machine(machine_id: str, update_req: MachineUpdateRequest, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """
    Update SOP and/or safety_text for a specific machine.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    
    changed = []
    if update_req.sop is not None:
        machine.sop = update_req.sop
        changed.append("sop")
    if update_req.safety_text is not None:
        machine.safety_text = update_req.safety_text
        changed.append("safety_text")
        
    if changed:
        session.add(machine)
        session.commit()
        session.refresh(machine)
        logger.info(f"Machine '{machine_id}' updated on /update endpoint. Changed fields: {', '.join(changed)}")
        
        # Log action
        log_action(session, "machine_update", "machine", machine_id, current_user.id, {"changed": changed})
        
        # Publish MQTT real-time notification
        payload = {
            "name": machine.name,
            "sop": machine.sop,
            "safety_text": machine.safety_text,
            "emergency": machine.emergency
        }
        publish_message(f"labcast/{machine_id}/config", payload)
        
    return machine

@router.post("/{machine_id}/emergency", response_model=MachineConfigResponse, dependencies=[Depends(RequireRole(["admin", "faculty", "technician"]))])
def set_emergency(machine_id: str, req: EmergencyRequest, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """
    Set the emergency flag for a specific machine.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    
    machine.emergency = req.emergency
    session.add(machine)
    session.commit()
    session.refresh(machine)
    
    logger.info(f"Machine '{machine_id}' emergency state set to {req.emergency} on /emergency endpoint.")
    
    # Log action
    log_action(session, "emergency_toggle", "machine", machine_id, current_user.id, {"emergency": req.emergency})
    
    # Publish MQTT real-time notification
    publish_message(f"labcast/{machine_id}/emergency", {"emergency": req.emergency})
    
    return machine

def chat_rate_limit() -> str:
    request = request_var.get()
    if request:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return "60/minute"
    return "5/minute"

@router.post("/{machine_id}/chat", response_model=ChatResponse)
@limiter.limit(chat_rate_limit)
def machine_chat(request: Request, machine_id: str, req: ChatRequest, session: Session = Depends(get_session), current_user: User | None = Depends(get_optional_user)):
    """
    Chat with the machine's manual context.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    
    # Log the chat
    user_id = current_user.id if current_user else "QR_STUDENT"
    log_action(session, "chat", "machine", machine_id, user_id, {"question": req.question[:100]})
    
    return process_chat_query(machine_id, req.question)
