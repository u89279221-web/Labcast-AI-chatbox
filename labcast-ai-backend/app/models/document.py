from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Document(SQLModel, table=True):
    """
    Model representing an uploaded document for a machine.
    """
    id: Optional[str] = Field(default=None, primary_key=True, description="Unique identifier for the document")
    machine_id: str = Field(foreign_key="machine.id", description="The machine this document belongs to")
    filename: str = Field(description="The original filename of the document")
    doc_type: str = Field(description="Type of document: manual, sop, safety, or maintenance")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the document was uploaded")
    extraction_method: str = Field(default="Standard", description="Method used to extract text: Standard or OCR")
    extracted_text: str = Field(default="", description="The text extracted from the document")
