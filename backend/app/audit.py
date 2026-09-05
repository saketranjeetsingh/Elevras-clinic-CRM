import json
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    organization_id: Optional[int],
    actor_user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    before: Optional[Dict[str, Any]],
    after: Optional[Dict[str, Any]],
    ip_address: Optional[str],
):
    """Log an audit event."""
    try:
        audit = AuditLog(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=json.dumps(before) if before else None,
            after=json.dumps(after) if after else None,
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP from request."""
    if request and request.client:
        return request.client.host
    return None