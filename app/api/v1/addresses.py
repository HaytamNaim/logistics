"""Delivery addresses CRUD."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DeliveryAddress, Zone
from app.core.rbac import require_permission
from app.schemas.address import DeliveryAddressCreate, DeliveryAddressUpdate, DeliveryAddressResponse
from app.core.audit import log_audit
from fastapi import Request

router = APIRouter(prefix="/delivery-addresses", tags=["delivery-addresses"])


@router.get("", response_model=list[DeliveryAddressResponse])
def list_addresses(
    zone_id: UUID | None = Query(None),
    current_user=Depends(require_permission("order", "read")),
    db=Depends(get_db),
):
    q = db.query(DeliveryAddress)
    if zone_id:
        q = q.filter(DeliveryAddress.zone_id == str(zone_id))
    return q.all()


@router.post("", response_model=DeliveryAddressResponse, status_code=201)
def create_address(
    body: DeliveryAddressCreate,
    request: Request,
    current_user=Depends(require_permission("order", "create")),
    db=Depends(get_db),
):
    addr = DeliveryAddress(**body.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    log_audit(db, current_user.id, "CREATE", "delivery_address", addr.id, None, addr.__dict__, request)
    return addr


@router.get("/{address_id}", response_model=DeliveryAddressResponse)
def get_address(
    address_id: UUID,
    current_user=Depends(require_permission("order", "read")),
    db=Depends(get_db),
):
    a = db.query(DeliveryAddress).filter(DeliveryAddress.id == str(address_id)).first()
    if not a:
        raise HTTPException(404, "Address not found")
    return a


@router.patch("/{address_id}", response_model=DeliveryAddressResponse)
def update_address(
    address_id: UUID,
    body: DeliveryAddressUpdate,
    request: Request,
    current_user=Depends(require_permission("order", "update")),
    db=Depends(get_db),
):
    a = db.query(DeliveryAddress).filter(DeliveryAddress.id == str(address_id)).first()
    if not a:
        raise HTTPException(404, "Address not found")
    old = {k: getattr(a, k) for k in body.model_dump(exclude_unset=True)}
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    log_audit(db, current_user.id, "UPDATE", "delivery_address", a.id, old, {k: getattr(a, k) for k in old}, request)
    return a
