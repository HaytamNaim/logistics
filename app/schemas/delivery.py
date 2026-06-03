from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from typing import Any


class DeliveryBase(BaseModel):
    order_id: UUID


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    failure_reason: str | None = None


class DeliveryStatusUpdate(BaseModel):
    status: str  # PREPARATION, IN_TRANSIT, DELIVERED, FAILED, RETURNED
    location: dict[str, float] | None = None  # { "lat": 1.0, "lng": 2.0 }
    proof: dict[str, Any] | None = None


class DeliveryAssign(BaseModel):
    driver_id: UUID


class DeliveryResponse(BaseModel):
    id: UUID
    order_id: UUID
    driver_id: UUID | None
    assigned_by: UUID | None
    assigned_at: datetime | None
    status: str
    status_changed_at: datetime | None
    estimated_distance_km: Decimal | None
    estimated_duration_mins: int | None
    estimated_arrival: datetime | None
    route_snapshot: dict | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
    status_history: list[dict] | None = None

    class Config:
        from_attributes = True
