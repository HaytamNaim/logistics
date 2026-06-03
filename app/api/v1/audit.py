"""GET /audit-logs — query audit trail (Admin)."""
from __future__ import annotations
from uuid import UUID
from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import desc
from app.database import get_db
from app.models import AuditLog
from app.core.rbac import get_current_user, get_user_roles, PERMISSIONS
from app.schemas.audit import AuditLogResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    resource_type: str | None = Query(None),
    resource_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    allowed = PERMISSIONS.get(("audit", "read"), [])
    roles = [r[0] for r in get_user_roles(db, str(current_user.id))]
    if not allowed or not any(r in allowed for r in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    q = db.query(AuditLog)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        q = q.filter(AuditLog.resource_id == str(resource_id))
    if user_id:
        q = q.filter(AuditLog.user_id == str(user_id))
    if from_date:
        from datetime import datetime
        q = q.filter(AuditLog.created_at >= datetime.fromisoformat(from_date.replace("Z", "+00:00")))
    if to_date:
        from datetime import datetime
        q = q.filter(AuditLog.created_at <= datetime.fromisoformat(to_date.replace("Z", "+00:00")))
    rows = q.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    return [AuditLogResponse.model_validate(r) for r in rows]
