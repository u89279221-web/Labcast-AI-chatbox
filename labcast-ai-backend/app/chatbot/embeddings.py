import logging
from sqlmodel import Session, select
from app.core.database import engine
from app.models.machine import Machine
from app.models.document import Document
from app.chatbot.retriever import retriever

logger = logging.getLogger(__name__)

def split_text_into_chunks(text: str, chunk_size: int = 250) -> list[str]:
    """Split text into chunks of roughly `chunk_size` words."""
    if not text:
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def reindex_machine(machine_id: str, session: Session):
    """Rebuilds the entire index for a given machine using its manual_text and all uploaded documents."""
    machine = session.get(Machine, machine_id)
    if not machine:
        return
    
    all_chunks = []
    
    # 1. Fallback / seed: manual_text
    if machine.manual_text:
        all_chunks.extend(split_text_into_chunks(machine.manual_text))
        
    # 2. Uploaded documents
    documents = session.exec(select(Document).where(Document.machine_id == machine_id)).all()
    for doc in documents:
        if doc.extracted_text:
            all_chunks.extend(split_text_into_chunks(doc.extracted_text))
            
    retriever.embed_and_index(machine_id, all_chunks)
    logger.info(f"Reindexed {len(all_chunks)} chunks for Machine '{machine_id}'")

def initialize_embeddings():
    """Load all machines and initialize their indexes."""
    logger.info("Initializing in-memory embeddings for all machines...")
    with Session(engine) as session:
        machines = session.exec(select(Machine)).all()
        for machine in machines:
            reindex_machine(machine.id, session)
    logger.info("Embeddings initialization complete.")
