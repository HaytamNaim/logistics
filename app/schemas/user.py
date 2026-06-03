from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserMe(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    roles: list[dict]  # [{ "code": "ADMIN", "scope_zone_id": null }]

    class Config:
        from_attributes = True
