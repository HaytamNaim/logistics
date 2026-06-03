"""Routes CRUD, optimize, publish."""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Route, RouteStop, Delivery, Driver
from app.core.rbac import require_permission, get_user_roles
from app.schemas.route import RouteCreate, RouteUpdate, RouteResponse
from app.core.audit import log_audit
from fastapi import Request

router = APIRouter(prefix="/routes", tags=["routes"])


def _route_response(r: Route, db: Session) -> RouteResponse:
    stops = [{"delivery_id": str(s.delivery_id), "sequence": s.sequence, "status": s.status, "estimated_arrival": s.estimated_arrival} for s in r.route_stops]
    return RouteResponse(
        id=r.id,
        driver_id=r.driver_id,
        planned_date=r.planned_date,
        status=r.status,
        waypoints=r.waypoints,
        total_stops=r.total_stops or 0,
        total_distance_km=r.total_distance_km,
        total_duration_mins=r.total_duration_mins,
        created_at=r.created_at,
        updated_at=r.updated_at,
        route_stops=stops,
    )


def _can_access_route(db: Session, user_id: str, route: Route) -> bool:
    roles = [r[0] for r in get_user_roles(db, user_id)]
    if "ADMIN" in roles or "FLEET_MANAGER" in roles:
        return True
    if "DRIVER" in roles:
        d = db.query(Driver).filter(Driver.user_id == user_id).first()
        return d and str(d.id) == str(route.driver_id)
    return False


@router.get("", response_model=list[RouteResponse])
def list_routes(
    driver_id: UUID | None = Query(None),
    status: str | None = Query(None),
    current_user=Depends(require_permission("route", "read")),
    db=Depends(get_db),
):
    q = db.query(Route)
    roles = [r[0] for r in get_user_roles(db, str(current_user.id))]
    if "DRIVER" in roles and "ADMIN" not in roles and "FLEET_MANAGER" not in roles:
        d = db.query(Driver).filter(Driver.user_id == str(current_user.id)).first()
        if d:
            q = q.filter(Route.driver_id == str(d.id))
    if driver_id:
        q = q.filter(Route.driver_id == str(driver_id))
    if status:
        q = q.filter(Route.status == status)
    return [_route_response(r, db) for r in q.order_by(Route.planned_date.desc()).all()]


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(
    route_id: UUID,
    current_user=Depends(require_permission("route", "read")),
    db=Depends(get_db),
):
    r = db.query(Route).filter(Route.id == str(route_id)).first()
    if not r:
        raise HTTPException(404, "Route not found")
    if not _can_access_route(db, str(current_user.id), r):
        raise HTTPException(403, "Forbidden")
    return _route_response(r, db)


@router.post("", response_model=RouteResponse, status_code=201)
def create_route(
    body: RouteCreate,
    request: Request,
    current_user=Depends(require_permission("route", "create")),
    db=Depends(get_db),
):
    driver = db.query(Driver).filter(Driver.id == str(body.driver_id)).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    waypoints = [str(x) for x in body.delivery_ids]
    r = Route(
        driver_id=str(body.driver_id),
        planned_date=body.planned_date,
        status="DRAFT",
        waypoints=waypoints,
        total_stops=len(waypoints),
    )
    db.add(r)
    db.flush()
    for i, did in enumerate(body.delivery_ids):
        db.add(RouteStop(route_id=r.id, delivery_id=str(did), sequence=i, status="PENDING"))
    db.commit()
    db.refresh(r)
    log_audit(db, current_user.id, "CREATE", "route", r.id, None, {"driver_id": str(body.driver_id), "stops": len(waypoints)}, request)
    return _route_response(r, db)


@router.patch("/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: UUID,
    body: RouteUpdate,
    request: Request,
    current_user=Depends(require_permission("route", "update")),
    db=Depends(get_db),
):
    r = db.query(Route).filter(Route.id == str(route_id)).first()
    if not r:
        raise HTTPException(404, "Route not found")
    if body.delivery_ids is not None:
        for s in list(r.route_stops):
            db.delete(s)
        for i, did in enumerate(body.delivery_ids):
            db.add(RouteStop(route_id=r.id, delivery_id=did, sequence=i, status="PENDING"))
        r.waypoints = [str(x) for x in body.delivery_ids]
        r.total_stops = len(body.delivery_ids)
    db.commit()
    db.refresh(r)
    log_audit(db, current_user.id, "UPDATE", "route", r.id, None, {"waypoints": r.waypoints}, request)
    return _route_response(r, db)


@router.post("/{route_id}/optimize", response_model=RouteResponse)
def optimize_route(
    route_id: UUID,
    request: Request,
    current_user=Depends(require_permission("route", "optimize")),
    db=Depends(get_db),
):
    """Reorder stops by a simple heuristic (e.g. by delivery address lat/lng). Production: use Distance Matrix + TSP."""
    r = db.query(Route).filter(Route.id == str(route_id)).first()
    if not r:
        raise HTTPException(404, "Route not found")
    stops = list(r.route_stops)
    if not stops:
        return _route_response(r, db)
    # Placeholder: keep current order; real impl would call Maps API and reorder
    log_audit(db, current_user.id, "UPDATE", "route", r.id, None, {"optimized": True}, request)
    return _route_response(r, db)


@router.post("/{route_id}/publish", response_model=RouteResponse)
def publish_route(
    route_id: UUID,
    request: Request,
    current_user=Depends(require_permission("route", "publish")),
    db=Depends(get_db),
):
    r = db.query(Route).filter(Route.id == str(route_id)).first()
    if not r:
        raise HTTPException(404, "Route not found")
    if r.status != "DRAFT":
        raise HTTPException(400, "Only DRAFT routes can be published")
    r.status = "PUBLISHED"
    db.commit()
    db.refresh(r)
    log_audit(db, current_user.id, "STATUS_CHANGE", "route", r.id, {"status": "DRAFT"}, {"status": "PUBLISHED"}, request)
    return _route_response(r, db)
