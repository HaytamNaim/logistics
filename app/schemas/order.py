from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class OrderItemBase(BaseModel):
    sku: str | None = None
    description: str | None = None
    quantity: int = 1
    weight_kg: Decimal = 0


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: UUID
    order_id: UUID

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    external_reference: str | None = None
    delivery_address_id: UUID
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    requested_delivery_start: datetime | None = None
    requested_delivery_end: datetime | None = None
    total_weight_kg: Decimal = 0
    notes: str | None = None


class OrderCreate(OrderBase):
    items: list[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    external_reference: str | None = None
    delivery_address_id: UUID | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    requested_delivery_start: datetime | None = None
    requested_delivery_end: datetime | None = None
    total_weight_kg: Decimal | None = None
    notes: str | None = None


class OrderTransition(BaseModel):
    to_status: str  # CONFIRMED, PREPARING, READY_FOR_PICKUP, CANCELLED


class OrderResponse(OrderBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    items: list[OrderItemResponse] = []
    delivery_address: dict | None = None  # filled by route
    delivery: dict | None = None

    class Config:
        from_attributes = True
