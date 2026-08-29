import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import RequireRole
from app.models.device import Device
from app.models.machine import Machine
from app.schemas.device import DeviceRegisterRequest, DeviceHeartbeatRequest, DeviceStatusResponse, FirmwareTemplateResponse, OtaTriggerRequest
from app.mqtt.publisher import publish_message

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/device",
    tags=["device"]
)

# Configurable timeout for offline status
OFFLINE_TIMEOUT_SECONDS = 15

def get_utc_now():
    # Helper to return aware UTC datetime for compatibility
    return datetime.now(timezone.utc)

@router.post("/register", response_model=DeviceStatusResponse)
def register_device(req: DeviceRegisterRequest, session: Session = Depends(get_session)):
    """
    Registers a new device or updates an existing one on boot.
    """
    # Verify machine exists
    machine = session.get(Machine, req.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
        
    device = session.get(Device, req.id)
    now = get_utc_now()
    
    if not device:
        device = Device(
            id=req.id,
            machine_id=req.machine_id,
            firmware_version=req.firmware_version,
            last_seen=now,
            status="online",
            config_version="1.0"
        )
        logger.info(f"Registered new device: {req.id} for machine {req.machine_id}")
    else:
        device.firmware_version = req.firmware_version
        device.last_seen = now
        device.status = "online"
        logger.info(f"Re-registered existing device: {req.id}")
        
    session.add(device)
    session.commit()
    session.refresh(device)
    
    return device

@router.post("/{device_id}/heartbeat", response_model=DeviceStatusResponse)
def device_heartbeat(device_id: str, req: DeviceHeartbeatRequest, session: Session = Depends(get_session)):
    """
    Called periodically by the hardware to prove it is online.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found. Register first.")
        
    device.last_seen = get_utc_now()
    device.status = "online"
    device.config_version = req.config_version
    device.wifi_signal = req.wifi_signal
    
    session.add(device)
    session.commit()
    session.refresh(device)
    
    return device

@router.get("/", response_model=list[DeviceStatusResponse], dependencies=[Depends(RequireRole(["admin", "technician"]))])
def list_devices(session: Session = Depends(get_session)):
    """
    Get a list of all devices and update their offline status dynamically on read.
    """
    devices = session.exec(select(Device)).all()
    now = get_utc_now()
    
    updated_devices = []
    for device in devices:
        last_seen_utc = device.last_seen
        if last_seen_utc.tzinfo is None:
            last_seen_utc = last_seen_utc.replace(tzinfo=timezone.utc)
            
        time_since_last_seen = now - last_seen_utc
        
        if device.status == "online" and time_since_last_seen > timedelta(seconds=OFFLINE_TIMEOUT_SECONDS):
            device.status = "offline"
            session.add(device)
            logger.warning(f"Device {device.id} marked offline (timeout in list).")
            
        updated_devices.append(device)
        
    session.commit()
    for d in updated_devices:
        session.refresh(d)
        
    return updated_devices

@router.get("/{device_id}/status", response_model=DeviceStatusResponse, dependencies=[Depends(RequireRole(["admin", "technician"]))])
def get_device_status(device_id: str, session: Session = Depends(get_session)):
    """
    Get the status of a device. Computed-on-read logic marks it offline if heartbeat is stale.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found.")
        
    now = get_utc_now()
    
    # Ensure both last_seen and now are aware datetimes for calculation if needed,
    # SQLModel might return naive datetimes depending on DB dialect.
    # To be safe, we compare strictly.
    last_seen_utc = device.last_seen
    if last_seen_utc.tzinfo is None:
        last_seen_utc = last_seen_utc.replace(tzinfo=timezone.utc)
        
    time_since_last_seen = now - last_seen_utc
    
    # Computed on read: transition to offline if timeout exceeded
    if device.status == "online" and time_since_last_seen > timedelta(seconds=OFFLINE_TIMEOUT_SECONDS):
        device.status = "offline"
        session.add(device)
        session.commit()
        session.refresh(device)
        logger.warning(f"Device {device_id} marked offline (timeout).")
        
    return device

@router.post("/{device_id}/test-message", dependencies=[Depends(RequireRole(["admin", "technician"]))])
def send_device_test_message(device_id: str, session: Session = Depends(get_session)):
    """
    Publishes a harmless test MQTT message to the device via the backend.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found.")
        
    payload = {"event": "test_ping", "timestamp": datetime.now(timezone.utc).isoformat()}
    publish_message(f"labcast/device/{device_id}/test", payload)
    return {"status": "success", "message": "Test MQTT message published."}

@router.post("/{device_id}/restart", dependencies=[Depends(RequireRole(["admin", "technician"]))])
def restart_device(device_id: str, session: Session = Depends(get_session)):
    """
    Publishes a remote restart command to MQTT for the target device.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found.")
        
    payload = {"command": "restart", "timestamp": datetime.now(timezone.utc).isoformat()}
    publish_message(f"labcast/device/{device_id}/command", payload)
    return {"status": "success", "message": "Remote restart command published."}

FIRMWARE_TEMPLATES = [
    {"id": "basic", "name": "LabCast Basic", "version": "1.0.0", "enabled_components": ["Core", "Wi-Fi"]},
    {"id": "mqtt", "name": "LabCast +MQTT", "version": "1.1.0", "enabled_components": ["Core", "Wi-Fi", "MQTT"]},
    {"id": "tft", "name": "LabCast +TFT", "version": "1.2.0", "enabled_components": ["Core", "Wi-Fi", "MQTT", "TFT Display"]},
    {"id": "sd", "name": "LabCast +SD", "version": "1.2.1", "enabled_components": ["Core", "Wi-Fi", "MQTT", "SD Card"]},
    {"id": "full", "name": "LabCast Full", "version": "2.0.0", "enabled_components": ["Core", "Wi-Fi", "MQTT", "TFT Display", "SD Card"]}
]

@router.get("/firmware/templates", response_model=list[FirmwareTemplateResponse], dependencies=[Depends(RequireRole(["admin", "technician", "faculty"]))])
def list_firmware_templates():
    """
    Get a list of all approved firmware templates.
    """
    return FIRMWARE_TEMPLATES

@router.post("/{device_id}/ota", dependencies=[Depends(RequireRole(["admin", "technician"]))])
def trigger_ota_update(device_id: str, req: OtaTriggerRequest, session: Session = Depends(get_session)):
    """
    Triggers an OTA update on the device by sending download configuration parameters over MQTT.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found.")
        
    template = next((t for t in FIRMWARE_TEMPLATES if t["id"] == req.template_id), None)
    if not template:
        raise HTTPException(status_code=400, detail=f"Firmware template '{req.template_id}' not found.")
        
    download_url = f"http://10.0.2.2:8001/static/firmware/{template['id']}.bin"
    sha256 = f"mock-sha256-hash-for-{template['id']}-binary-file"
    
    payload = {
        "download_url": download_url,
        "sha256": sha256,
        "version": template["version"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    publish_message(f"labcast/device/{device_id}/ota", payload)
    return {"status": "success", "message": f"OTA update triggered for device {device_id} using template {template['name']}."}

@router.delete("/{device_id}", dependencies=[Depends(RequireRole(["admin"]))])
def revoke_device(device_id: str, session: Session = Depends(get_session)):
    """
    Deletes (revokes) a device from the database.
    """
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found.")
        
    session.delete(device)
    session.commit()
    return {"status": "success", "message": f"Device {device_id} revoked successfully."}



