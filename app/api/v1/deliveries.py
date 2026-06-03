"""Deliveries CRUD, status FSM, assign, assign-auto, WebSocket track."""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models import Delivery, DeliveryStatusHistory, Order, DeliveryAddress, Driver
from app.core.rbac import get_current_user, require_permission, get_user_roles
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryResponse, DeliveryStatusUpdate, DeliveryAssign
from app.core.audit import log_audit
from app.services.delivery_state import can_transition as delivery_can_transition
from fastapi import Request
import json

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


def _delivery_to_response(d: Delivery, include_history: bool = False) -> DeliveryResponse:
    hist = None
    if include_history and d.status_history:
        hist = [
            {"status": h.status, "previous_status": h.previous_status, "created_at": h.created_at.isoformat()}
            for h in d.status_history
        ]
    return DeliveryResponse(
        id=d.id,
        order_id=d.order_id,
        driver_id=d.driver_id,
        assigned_by=d.assigned_by,
        assigned_at=d.assigned_at,
        status=d.status,
        status_changed_at=d.status_changed_at,
        estimated_distance_km=d.estimated_distance_km,
        estimated_duration_mins=d.estimated_duration_mins,
        estimated_arrival=d.estimated_arrival,
        route_snapshot=d.route_snapshot,
        failure_reason=d.failure_reason,
        created_at=d.created_at,
        updated_at=d.updated_at,
        status_history=hist,
    )


def _driver_can_see_delivery(db: Session, user_id: str, delivery: Delivery) -> bool:
    roles = get_user_roles(db, user_id)
    codes = [r[0] for r in roles]
    if "ADMIN" in codes or "FLEET_MANAGER" in codes:
        return True
    if "DRIVER" in codes and delivery.driver_id:
        driver = db.query(Driver).filter(Driver.user_id == user_id).first()
        return driver and str(driver.id) == str(delivery.driver_id)
    return False


@router.get("", response_model=list[DeliveryResponse])
def list_deliveries(
    status: str | None = Query(None),
    driver_id: UUID | None = Query(None),
    zone_id: UUID | None = Query(None),
    current_user=Depends(require_permission("delivery", "read")),
      db=Depends(get_db),
):
    q = db.query(Delivery)
    roles = [r[0] for r in get_user_roles(db, str(current_user.id))]
    if "DRIVER" in roles and "ADMIN" not in roles and "FLEET_MANAGER" not in roles:
        driver = db.query(Driver).filter(Driver.user_id == str(current_user.id)).first()
        if driver:
            q = q.filter(Delivery.driver_id == str(driver.id))
    if status:
        q = q.filter(Delivery.status == status)
    if driver_id:
        q = q.filter(Delivery.driver_id == str(driver_id))
    if zone_id:
        q = q.join(Order).join(DeliveryAddress).filter(DeliveryAddress.zone_id == str(zone_id))
    rows = q.order_by(Delivery.created_at.desc()).all()
    return [_delivery_to_response(r) for r in rows]


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: UUID,
    current_user=Depends(require_permission("delivery", "read")),
      db=Depends(get_db),
):
    d = db.query(Delivery).filter(Delivery.id == str(delivery_id)).first()
    if not d:
        raise HTTPException(404, "Delivery not found")
    if not _driver_can_see_delivery(db, str(current_user.id), d):
        raise HTTPException(403, "Cannot access this delivery")
    return _delivery_to_response(d, include_history=True)


@router.post("", response_model=DeliveryResponse, status_code=201)
def create_delivery(
    body: DeliveryCreate,
    request: Request,
    current_user=Depends(require_permission("delivery", "create")),
      db=Depends(get_db),
):
    existing = db.query(Delivery).filter(Delivery.order_id == str(body.order_id)).first()
    if existing:
        return _delivery_to_response(existing)
    order = db.query(Order).filter(Order.id == str(body.order_id)).first()
    if not order:
        raise HTTPException(404, "Order not found")
    d = Delivery(order_id=body.order_id, status="PREPARATION")
    db.add(d)
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "CREATE", "delivery", d.id, None, {"order_id": str(body.order_id), "status": "PREPARATION"}, request)
    return _delivery_to_response(d)


@router.patch("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: UUID,
    body: DeliveryUpdate,
    request: Request,
    current_user=Depends(require_permission("delivery", "update")),
      db=Depends(get_db),
):
    d = db.query(Delivery).filter(Delivery.id == str(delivery_id)).first()
    if not d:
        raise HTTPException(404, "Delivery not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "UPDATE", "delivery", d.id, None, {"failure_reason": d.failure_reason}, request)
    return _delivery_to_response(d)


@router.post("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: UUID,
    body: DeliveryStatusUpdate,
    request: Request,
  current_user=Depends(require_permission("delivery", "status")),
    db=Depends(get_db),
):
    d = db.query(Delivery).filter(Delivery.id == str(delivery_id)).first()
    if not d:
        raise HTTPException(404, "Delivery not found")
    if not _driver_can_see_delivery(db, str(current_user.id), d):
        raise HTTPException(403, "Cannot update this delivery")
    if not delivery_can_transition(d.status, body.status):
        raise HTTPException(400, f"Invalid transition from {d.status} to {body.status}")
    prev = d.status
    d.status = body.status
    d.status_changed_at = datetime.utcnow()
    if body.location and d.driver_id:
        dr = db.query(Driver).filter(Driver.id == d.driver_id).first()
        if dr:
            dr.current_location = body.location
            dr.last_availability_updated = datetime.utcnow()
    db.add(DeliveryStatusHistory(
        delivery_id=d.id,
        status=body.status,
        previous_status=prev,
        payload=body.proof or body.location,
        changed_by=str(current_user.id),
    ))
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "STATUS_CHANGE", "delivery", d.id, {"status": prev}, {"status": body.status}, request)
    return _delivery_to_response(d, include_history=True)


@router.post("/{delivery_id}/assign", response_model=DeliveryResponse)
def assign_driver(
    delivery_id: UUID,
    body: DeliveryAssign,
    request: Request,
    current_user=Depends(require_permission("delivery", "assign")),
      db=Depends(get_db),
):
    d = db.query(Delivery).filter(Delivery.id == str(delivery_id)).first()
    if not d:
        raise HTTPException(404, "Delivery not found")
    driver = db.query(Driver).filter(Driver.id == str(body.driver_id)).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    old_driver = d.driver_id
    d.driver_id = str(body.driver_id)
    d.assigned_by = str(current_user.id)
    d.assigned_at = datetime.utcnow()
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "ASSIGN", "delivery", d.id, {"driver_id": old_driver}, {"driver_id": str(body.driver_id)}, request)
    return _delivery_to_response(d)


@router.post("/assign-auto", response_model=dict)
def trigger_auto_assign(
    request: Request,
    current_user=Depends(require_permission("delivery", "assign_auto")),
    db=Depends(get_db),
):
    from app.services.auto_assign import run_auto_assign
    result = run_auto_assign(db)
    log_audit(db, current_user.id, "ASSIGN", "delivery", None, None, {"auto_assign": result}, request)
    return result


@router.post("/{delivery_id}/location")
def delivery_location_heartbeat(
    delivery_id: UUID,
    body: dict,  # { "lat": float, "lng": float }
    current_user=Depends(require_permission("delivery", "status")),
    db=Depends(get_db),
):
    d = db.query(Delivery).filter(Delivery.id == str(delivery_id)).first()
    if not d:
        raise HTTPException(404, "Delivery not found")
    if not _driver_can_see_delivery(db, str(current_user.id), d):
        raise HTTPException(403, "Forbidden")
    if d.status != "IN_TRANSIT":
        raise HTTPException(400, "Delivery is not in transit")
    lat = body.get("lat")
    lng = body.get("lng")
    if lat is None or lng is None:
        raise HTTPException(400, "lat and lng required")
    driver = db.query(Driver).filter(Driver.id == d.driver_id).first()
    if driver:
        driver.current_location = {"lat": float(lat), "lng": float(lng), "updated_at": datetime.utcnow().isoformat()}
        driver.last_availability_updated = datetime.utcnow()
    db.commit()
    return {"ok": True}


@router.websocket("/{delivery_id}/track")
async def track_websocket(websocket: WebSocket, delivery_id: str):
    """Simple WebSocket: clients connect to receive status/location updates. Auth via query or header in production."""
    await websocket.accept()
    try:
        while True:
            # In production: subscribe to Redis pub/sub for this delivery_id and forward to client
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        pass
