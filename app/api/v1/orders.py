"""Orders CRUD and state transitions."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models import Order, OrderItem, DeliveryAddress
from app.core.rbac import get_current_user, require_permission
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemResponse, OrderTransition
from app.core.audit import log_audit
from app.services.order_state import can_transition as order_can_transition
from fastapi import Request

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_to_response(o: Order, db: Session) -> OrderResponse:
    items = [OrderItemResponse.model_validate(i) for i in o.order_items]
    addr = None
    if o.delivery_address:
        addr = {"id": str(o.delivery_address.id), "line1": o.delivery_address.line1, "city": o.delivery_address.city}
    d = None
    if o.delivery:
        d = {"id": str(o.delivery.id), "status": o.delivery.status, "driver_id": str(o.delivery.driver_id) if o.delivery.driver_id else None}
    return OrderResponse(
        id=o.id,
        external_reference=o.external_reference,
        delivery_address_id=o.delivery_address_id,
        customer_name=o.customer_name,
        customer_phone=o.customer_phone,
        customer_email=o.customer_email,
        status=o.status,
        requested_delivery_start=o.requested_delivery_start,
        requested_delivery_end=o.requested_delivery_end,
        total_weight_kg=o.total_weight_kg,
        notes=o.notes,
        created_at=o.created_at,
        updated_at=o.updated_at,
        created_by=o.created_by,
        items=items,
        delivery_address=addr,
        delivery=d,
    )


@router.get("", response_model=list[OrderResponse])
def list_orders(
    status: str | None = Query(None),
    zone_id: UUID | None = Query(None),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    search: str | None = Query(None),
    current_user=Depends(require_permission("order", "read")),
    db=Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    needs_addr_join = zone_id or from_date or to_date or search
    if needs_addr_join:
        q = q.join(DeliveryAddress, Order.delivery_address_id == DeliveryAddress.id)
        if zone_id:
            q = q.filter(DeliveryAddress.zone_id == str(zone_id))
        if from_date:
            q = q.filter(Order.requested_delivery_start >= datetime.fromisoformat(from_date.replace("Z", "+00:00")))
        if to_date:
            q = q.filter(Order.requested_delivery_end <= datetime.fromisoformat(to_date.replace("Z", "+00:00")))
        if search:
            term = f"%{search}%"
            q = q.filter(or_(
                Order.external_reference.ilike(term),
                Order.customer_name.ilike(term),
                DeliveryAddress.line1.ilike(term),
                DeliveryAddress.city.ilike(term),
            ))
    orders = q.order_by(Order.created_at.desc()).all()
    return [_order_to_response(o, db) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    current_user=Depends(require_permission("order", "read")),
    db=Depends(get_db),
):
    o = db.query(Order).filter(Order.id == str(order_id)).first()
    if not o:
        raise HTTPException(404, "Order not found")
    return _order_to_response(o, db)


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    body: OrderCreate,
    request: Request,
    current_user=Depends(require_permission("order", "create")),
    db=Depends(get_db),
):
    items_data = body.items
    payload = body.model_dump(exclude={"items"})
    order = Order(**payload, created_by=str(current_user.id))
    db.add(order)
    db.flush()
    for it in items_data:
        db.add(OrderItem(**it.model_dump(), order_id=order.id))
    db.commit()
    db.refresh(order)
    log_audit(db, current_user.id, "CREATE", "order", order.id, None, {"status": order.status, "delivery_address_id": str(order.delivery_address_id)}, request)
    return _order_to_response(order, db)


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: UUID,
    body: OrderUpdate,
    request: Request,
    current_user=Depends(require_permission("order", "update")),
    db=Depends(get_db),
):
    o = db.query(Order).filter(Order.id == str(order_id)).first()
    if not o:
        raise HTTPException(404, "Order not found")
    old = {k: getattr(o, k) for k in body.model_dump(exclude_unset=True)}
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    log_audit(db, current_user.id, "UPDATE", "order", o.id, old, {k: getattr(o, k) for k in old}, request)
    return _order_to_response(o, db)


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: UUID,
    request: Request,
    current_user=Depends(require_permission("order", "delete")),
    db=Depends(get_db),
):
    o = db.query(Order).filter(Order.id == str(order_id)).first()
    if not o:
        raise HTTPException(404, "Order not found")
    old = {"id": str(o.id), "status": o.status}
    db.delete(o)
    db.commit()
    log_audit(db, current_user.id, "DELETE", "order", order_id, old, None, request)
    return None


@router.post("/{order_id}/transition", response_model=OrderResponse)
def order_transition(
    order_id: UUID,
    body: OrderTransition,
    request: Request,
    current_user=Depends(require_permission("order", "transition")),
    db=Depends(get_db),
):
    o = db.query(Order).filter(Order.id == str(order_id)).first()
    if not o:
        raise HTTPException(404, "Order not found")
    if not order_can_transition(o.status, body.to_status):
        raise HTTPException(400, f"Invalid transition from {o.status} to {body.to_status}")
    old_status = o.status
    o.status = body.to_status
    db.commit()
    db.refresh(o)
    log_audit(db, current_user.id, "STATUS_CHANGE", "order", o.id, {"status": old_status}, {"status": body.to_status}, request)
    return _order_to_response(o, db)
