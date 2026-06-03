from uuid import UUID
from pydantic import BaseModel
from typing import Any


class ZoneBase(BaseModel):
    name: str
    polygon: dict[str, Any] | None = None
    parent_zone_id: UUID | None = None


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: str | None = None
    polygon: dict[str, Any] | None = None
    parent_zone_id: UUID | None = None


class ZoneResponse(ZoneBase):
    id: UUID

    class Config:
        from_attributes = True
