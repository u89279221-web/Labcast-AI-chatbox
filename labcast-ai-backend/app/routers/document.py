from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
import uuid
import logging

from app.core.database import get_session
from app.core.deps import RequireRole, get_current_user
from app.models.machine import Machine
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.chatbot.ingest import process_upload
from app.chatbot.embeddings import reindex_machine
from app.core.audit import log_action

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{machine_id}/documents", response_model=list[DocumentResponse], dependencies=[Depends(RequireRole(["admin", "faculty"]))])
def list_documents(machine_id: str, session: Session = Depends(get_session)):
    """List all documents for a given machine."""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
        
    documents = session.exec(select(Document).where(Document.machine_id == machine_id)).all()
    return documents

@router.post("/{machine_id}/documents", response_model=DocumentUploadResponse, dependencies=[Depends(RequireRole(["admin", "faculty"]))])
async def upload_document(
    machine_id: str, 
    file: UploadFile = File(...),
    doc_type: str = Form("manual"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload a new document (PDF, TXT, etc.), extract text via pypdf/OCR, save it, and reindex."""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
        
    file_bytes = await file.read()
    
    # Run the ingestion pipeline (PDF parsing, OCR fallback, cleaning)
    extracted_text, extraction_method = process_upload(file_bytes, file.filename)
    
    if not extracted_text:
        # We don't fail completely, but we let them know it was empty
        logger.warning(f"No text could be extracted from {file.filename}")
        
    doc_id = str(uuid.uuid4())
    document = Document(
        id=doc_id,
        machine_id=machine_id,
        filename=file.filename,
        doc_type=doc_type,
        extracted_text=extracted_text,
        extraction_method=extraction_method
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    # Reindex the machine with the new document included
    reindex_machine(machine_id, session)
    
    log_action(session, "upload_document", "document", doc_id, current_user.id, {"filename": file.filename, "machine_id": machine_id})
    
    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        message="Document processed and indexed successfully.",
        extracted_length=len(extracted_text),
        extraction_method=extraction_method
    )

@router.delete("/{machine_id}/documents/{document_id}", dependencies=[Depends(RequireRole(["admin", "faculty"]))])
def delete_document(
    machine_id: str,
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a document from the database and reindex machine embeddings."""
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
        
    doc = session.get(Document, document_id)
    if not doc or doc.machine_id != machine_id:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found for machine '{machine_id}'.")
        
    filename = doc.filename
    session.delete(doc)
    session.commit()
    
    # Reindex embeddings without the deleted document
    reindex_machine(machine_id, session)
    
    log_action(session, "delete_document", "document", document_id, current_user.id, {"filename": filename, "machine_id": machine_id})
    
    return {"message": f"Document '{filename}' deleted from database and un-indexed."}
