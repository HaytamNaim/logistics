from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditLogQuery(BaseModel):
    resource_type: str | None = None
    resource_id: UUID | None = None
    user_id: UUID | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    limit: int = 100
    offset: int = 0


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    old_value: dict | None
    new_value: dict | None
    client_ip: str | None
    user_agent: str | None
    created_at: datetime

    class Config:
        from_attributes = True
