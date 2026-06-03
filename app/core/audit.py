"""Audit logging: write to audit_logs table."""
import json
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Request
from app.models import AuditLog


def sanitize_for_audit(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Optionally mask PII in old_value/new_value."""
    if data is None:
        return None
    out = dict(data)
    for key in ("customer_phone", "customer_email", "password_hash"):
        if key in out and out[key] is not None:
            out[key] = "[REDACTED]"
    return out


def log_audit(
    db: Session,
    user_id: UUID | str | None,
    action: str,
    resource_type: str,
    resource_id: UUID | str | None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    """Append one row to audit_logs."""
    client_ip = None
    user_agent = None
    if request:
        client_ip = request.client.host if request.client else None
        user_agent = (request.headers.get("user-agent") or "")[:512]
    entry = AuditLog(
        user_id=str(user_id) if user_id else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        old_value=sanitize_for_audit(old_value),
        new_value=sanitize_for_audit(new_value),
        client_ip=client_ip,
        user_agent=user_agent,
    )
    db.add(entry)
    db.commit()
