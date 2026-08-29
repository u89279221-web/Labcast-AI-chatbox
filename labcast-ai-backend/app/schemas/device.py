from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DeviceRegisterRequest(BaseModel):
    id: str
    machine_id: str
    firmware_version: str

class DeviceHeartbeatRequest(BaseModel):
    config_version: str
    wifi_signal: Optional[int] = None

class DeviceStatusResponse(BaseModel):
    id: str
    machine_id: str
    status: str
    last_seen: datetime
    config_version: str
    wifi_signal: Optional[int] = None

class FirmwareTemplateResponse(BaseModel):
    id: str
    name: str
    version: str
    enabled_components: List[str]

class OtaTriggerRequest(BaseModel):
    template_id: str
