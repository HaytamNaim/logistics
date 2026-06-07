"""Audit logging: write to audit_logs table."""
import json
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Request
from app.models import AuditLog


_PII_PATTERNS = (
    "password", "secret", "token", "key", "phone", "email",
    "address", "ssn", "dob", "birth", "credit", "card", "cvv", "pin",
)


def sanitize_for_audit(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Optionally mask PII in old_value/new_value."""
    if data is None:
        return None
    out = {}
    for k, v in data.items():
        if any(pattern in k.lower() for pattern in _PII_PATTERNS):
            out[k] = "[REDACTED]"
        elif isinstance(v, dict):
            out[k] = sanitize_for_audit(v)
        else:
            out[k] = v
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
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.headers.get("X-Real-IP") or (request.client.host if request.client else None)
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
