from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class DeliveryAddressBase(BaseModel):
    line1: str
    line2: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str = "US"
    lat: Decimal | None = None
    lng: Decimal | None = None
    zone_id: UUID | None = None


class DeliveryAddressCreate(DeliveryAddressBase):
    pass


class DeliveryAddressUpdate(BaseModel):
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    zone_id: UUID | None = None


class DeliveryAddressResponse(DeliveryAddressBase):
    id: UUID

    class Config:
        from_attributes = True
