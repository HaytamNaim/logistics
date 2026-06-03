"""Analytics KPIs: delivery speed, delay rate, driver efficiency."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Delivery, Order, Driver, DeliveryAddress
from app.core.rbac import require_permission
from app.schemas.analytics import KPIsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpis", response_model=KPIsResponse)
def get_kpis(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    zone_id: str | None = Query(None),
    driver_id: str | None = Query(None),
    current_user=Depends(require_permission("analytics", "read")),
    db=Depends(get_db),
):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    if from_date:
        start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
    if to_date:
        end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))

    q = db.query(Delivery).filter(
        Delivery.status.in_(["DELIVERED", "FAILED", "RETURNED"]),
        Delivery.assigned_at >= start,
        Delivery.assigned_at <= end,
    )
    if driver_id:
        q = q.filter(Delivery.driver_id == driver_id)
    if zone_id:
        q = q.join(Order, Delivery.order_id == Order.id).join(DeliveryAddress, Order.delivery_address_id == DeliveryAddress.id).filter(DeliveryAddress.zone_id == zone_id)

    rows = q.all()
    delivered = [r for r in rows if r.status == "DELIVERED"]
    delays = 0
    total_mins = 0.0
    for r in delivered:
        if r.assigned_at and r.status_changed_at:
            duration_mins = (r.status_changed_at - r.assigned_at).total_seconds() / 60
            total_mins += duration_mins
        if r.order and r.order.requested_delivery_end and r.status_changed_at:
            if r.status_changed_at > r.order.requested_delivery_end:
                delays += 1
    delay_rate = delays / len(delivered) if delivered else None
    speed_avg = total_mins / len(delivered) if delivered else None

    # Driver utilization: available-minutes vs busy-minutes (simplified)
    drivers = db.query(Driver).count()
    utilization = len(delivered) / (drivers * 30 * 8 * 60) * 480 if drivers else None  # placeholder

    return KPIsResponse(
        delivery_speed_avg_mins=speed_avg,
        delay_rate=delay_rate,
        driver_utilization=utilization,
        dimensions={"from_date": start.isoformat(), "to_date": end.isoformat(), "zone_id": zone_id, "driver_id": driver_id},
    )


@router.get("/deliveries")
def get_delivery_metrics(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    current_user=Depends(require_permission("analytics", "read")),
    db=Depends(get_db),
):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    if from_date:
        start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
    if to_date:
        end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
    counts = db.query(Delivery.status, func.count(Delivery.id)).filter(
        Delivery.created_at >= start,
        Delivery.created_at <= end,
    ).group_by(Delivery.status).all()
    return {"by_status": {s: c for s, c in counts}, "from": start.isoformat(), "to": end.isoformat()}


@router.get("/drivers")
def get_driver_metrics(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    current_user=Depends(require_permission("analytics", "read")),
    db=Depends(get_db),
):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    if from_date:
        start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
    if to_date:
        end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
    rows = db.query(Delivery.driver_id, func.count(Delivery.id)).filter(
        Delivery.status == "DELIVERED",
        Delivery.status_changed_at >= start,
        Delivery.status_changed_at <= end,
        Delivery.driver_id.isnot(None),
    ).group_by(Delivery.driver_id).all()
    return {"deliveries_per_driver": [{"driver_id": d, "count": c} for d, c in rows], "from": start.isoformat(), "to": end.isoformat()}
