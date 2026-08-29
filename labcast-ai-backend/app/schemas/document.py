from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    machine_id: str
    filename: str
    doc_type: str
    uploaded_at: datetime
    extraction_method: Optional[str] = "Standard"
    # We do not include extracted_text in the list response to keep it small

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    message: str
    extracted_length: int
    extraction_method: str
