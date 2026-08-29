import logging
import json
from typing import Optional, Any
from sqlmodel import Session
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

def log_action(
    session: Session, 
    action: str, 
    target_type: str, 
    target_id: str, 
    user_id: Optional[str] = None, 
    details: Optional[Any] = None
) -> None:
    """
    Helper to synchronously create an AuditLog record.
    `details` can be a dict which will be JSON serialized.
    """
    try:
        details_str = None
        if details is not None:
            if isinstance(details, (dict, list)):
                details_str = json.dumps(details)
            else:
                details_str = str(details)
                
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details_str
        )
        session.add(log_entry)
        session.commit()
    except Exception as e:
        # Don't fail the primary transaction just because logging failed, 
        # but do log it to stdout.
        logger.error(f"Failed to write audit log for action '{action}': {e}")
        session.rollback()
