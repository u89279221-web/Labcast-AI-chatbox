"""
Pydantic schemas for the Machine model.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class MachineConfigResponse(BaseModel):
    name: str
    sop: List[str]
    safety_text: str
    emergency: bool

class MachineUpdateRequest(BaseModel):
    sop: Optional[List[str]] = Field(None, max_length=20, description="List of max 20 SOP steps")
    safety_text: Optional[str] = Field(None, max_length=2000, description="Safety text, max 2000 chars")

class EmergencyRequest(BaseModel):
    emergency: bool

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="Chat question, max 500 chars")

class ChatResponse(BaseModel):
    answer: str
    source_snippet: str
