from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Device(SQLModel, table=True):
    """
    Model representing a hardware device (e.g. ESP32).
    """
    id: Optional[str] = Field(default=None, primary_key=True, description="Unique identifier for the device, e.g., 'ESP32-CNC01'")
    machine_id: str = Field(foreign_key="machine.id", description="The machine this device controls")
    firmware_version: str = Field(description="The firmware version running on the device")
    last_seen: datetime = Field(description="Timestamp of the last successful heartbeat (UTC)")
    status: str = Field(description="Current status: 'online' or 'offline'")
    config_version: str = Field(default="1.0", description="Configuration version")
    wifi_signal: Optional[int] = Field(default=None, description="Wi-Fi signal strength (RSSI)")
