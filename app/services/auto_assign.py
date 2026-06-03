"""Automatic driver assignment for unassigned deliveries (PREPARATION, no driver_id)."""
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session
from app.models import Delivery, Driver, Order, DeliveryAddress


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km between two (lat, lng) points."""
    R = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def run_auto_assign(db: Session) -> dict:
    """
    Fetch unassigned deliveries (PREPARATION, driver_id IS NULL),
    fetch available drivers (status=AVAILABLE, auto_assign_eligible),
    score by proximity (simple distance) and workload, assign best driver.
    Returns { "assigned": n, "delivery_ids": [...], "unassigned": [...] }.
    """
    now = datetime.utcnow()
    horizon = now + timedelta(hours=8)

    # Unassigned deliveries with requested time in window
    unassigned = (
        db.query(Delivery)
        .join(Order, Delivery.order_id == Order.id)
        .filter(
            Delivery.driver_id.is_(None),
            Delivery.status == "PREPARATION",
            Order.requested_delivery_start <= horizon,
        )
        .order_by(Order.requested_delivery_start)
        .all()
    )

    available = (
        db.query(Driver)
        .filter(Driver.status == "AVAILABLE", Driver.auto_assign_eligible.is_(True))
        .all()
    )

    assigned_ids = []
    still_unassigned = []

    for d in unassigned:
        order = d.order
        addr = order.delivery_address
        zone_id = str(addr.zone_id) if addr and addr.zone_id else None

        # Filter drivers by zone if we had zone-scoped drivers (simplified: use all available)
        candidates = [
            dr
            for dr in available
            if dr.status == "AVAILABLE"
        ]

        if not candidates:
            still_unassigned.append(str(d.id))
            continue

        # Score: prefer drivers with fewer deliveries today, then by great-circle distance
        def dist(a: dict | None, b_lat, b_lng) -> float:
            if not a or b_lat is None or b_lng is None:
                return 0.0
            la, ln = a.get("lat"), a.get("lng")
            if la is None or ln is None:
                return 0.0
            return _haversine_km(float(la), float(ln), float(b_lat), float(b_lng))

        addr_lat = float(addr.lat) if addr and addr.lat is not None else None
        addr_lng = float(addr.lng) if addr and addr.lng is not None else None

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        workloads = {}
        for dr in candidates:
            count = db.query(Delivery).filter(
                Delivery.driver_id == str(dr.id),
                Delivery.assigned_at >= today_start,
            ).count()
            workloads[str(dr.id)] = count

        def score(dr: Driver) -> tuple:
            w = workloads.get(str(dr.id), 0)
            d = dist(dr.current_location, addr_lat, addr_lng)
            return (-w, d)  # lower workload first, then closer

        best = min(candidates, key=score)
        d.driver_id = str(best.id)
        d.assigned_by = None  # system
        d.assigned_at = now
        assigned_ids.append(str(d.id))
        best.status = "BUSY"
        available = [x for x in available if x.id != best.id]

    db.commit()
    return {"assigned": len(assigned_ids), "delivery_ids": assigned_ids, "unassigned": still_unassigned}
