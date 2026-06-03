from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from typing import Any


class RouteBase(BaseModel):
    driver_id: UUID
    planned_date: datetime
    delivery_ids: list[UUID] = []  # ordered for waypoints


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    delivery_ids: list[UUID] | None = None  # reorder/add/remove


class RouteResponse(BaseModel):
    id: UUID
    driver_id: UUID
    planned_date: datetime
    status: str
    waypoints: list | None
    total_stops: int
    total_distance_km: Decimal | None
    total_duration_mins: int | None
    created_at: datetime
    updated_at: datetime
    route_stops: list[dict] | None = None

    class Config:
        from_attributes = True
