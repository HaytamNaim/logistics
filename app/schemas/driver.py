from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Any


class DriverBase(BaseModel):
    license_number: str | None = None
    phone: str | None = None
    auto_assign_eligible: bool = True


class DriverUpdate(BaseModel):
    license_number: str | None = None
    phone: str | None = None
    auto_assign_eligible: bool | None = None


class DriverAvailability(BaseModel):
    status: str  # AVAILABLE, BUSY, OFF_DUTY, BREAK
    location: dict[str, float] | None = None  # { "lat", "lng" }


class DriverResponse(DriverBase):
    id: UUID
    user_id: UUID
    status: str
    current_location: dict | None
    last_availability_updated: datetime | None
    user: dict | None = None  # { "email", "full_name" }

    class Config:
        from_attributes = True
