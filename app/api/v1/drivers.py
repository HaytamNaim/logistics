"""Drivers CRUD, availability, available snapshot."""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Driver, User
from app.core.rbac import get_current_user, require_permission, get_user_roles
from app.schemas.driver import DriverUpdate, DriverResponse, DriverAvailability
from app.core.audit import log_audit
from fastapi import Request

router = APIRouter(prefix="/drivers", tags=["drivers"])


def _driver_response(d: Driver, db: Session) -> DriverResponse:
    user = db.query(User).filter(User.id == d.user_id).first()
    u = {"email": user.email, "full_name": user.full_name} if user else None
    return DriverResponse(
        id=d.id,
        user_id=d.user_id,
        license_number=d.license_number,
        phone=d.phone,
        status=d.status,
        current_location=d.current_location,
        last_availability_updated=d.last_availability_updated,
        auto_assign_eligible=d.auto_assign_eligible,
        user=u,
    )


def _driver_can_access(db: Session, user_id: str, driver_id: str) -> bool:
    roles = [r[0] for r in get_user_roles(db, user_id)]
    if "ADMIN" in roles or "FLEET_MANAGER" in roles:
        return True
    if "DRIVER" in roles:
        d = db.query(Driver).filter(Driver.user_id == user_id).first()
        return d and str(d.id) == driver_id
    return False


@router.get("", response_model=list[DriverResponse])
def list_drivers(
    status: str | None = Query(None),
    auto_assign_eligible: bool | None = Query(None),
    current_user=Depends(require_permission("driver", "read")),
    db=Depends(get_db),
):
    q = db.query(Driver)
    roles = [r[0] for r in get_user_roles(db, str(current_user.id))]
    if "DRIVER" in roles and "ADMIN" not in roles and "FLEET_MANAGER" not in roles:
        q = q.filter(Driver.user_id == str(current_user.id))
    if status:
        q = q.filter(Driver.status == status)
    if auto_assign_eligible is not None:
        q = q.filter(Driver.auto_assign_eligible == auto_assign_eligible)
    return [_driver_response(d, db) for d in q.all()]


@router.get("/available", response_model=list[DriverResponse])
def list_available_drivers(
    zone_id: UUID | None = Query(None),
    current_user=Depends(require_permission("driver", "read")),
    db=Depends(get_db),
):
    q = db.query(Driver).filter(Driver.status == "AVAILABLE", Driver.auto_assign_eligible.is_(True))
    return [_driver_response(d, db) for d in q.all()]


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: UUID,
    current_user=Depends(require_permission("driver", "read")),
    db=Depends(get_db),
):
    d = db.query(Driver).filter(Driver.id == str(driver_id)).first()
    if not d:
        raise HTTPException(404, "Driver not found")
    if not _driver_can_access(db, str(current_user.id), str(driver_id)):
        raise HTTPException(403, "Forbidden")
    return _driver_response(d, db)


@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: UUID,
    body: DriverUpdate,
    request: Request,
    current_user=Depends(require_permission("driver", "update")),
    db=Depends(get_db),
):
    d = db.query(Driver).filter(Driver.id == str(driver_id)).first()
    if not d:
        raise HTTPException(404, "Driver not found")
    roles = [r[0] for r in get_user_roles(db, str(current_user.id))]
    if "DRIVER" in roles and "ADMIN" not in roles and "FLEET_MANAGER" not in roles and "DISPATCHER" not in roles:
        if d.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
    old = {k: getattr(d, k) for k in body.model_dump(exclude_unset=True)}
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "UPDATE", "driver", d.id, old, {k: getattr(d, k) for k in old}, request)
    return _driver_response(d, db)


@router.post("/{driver_id}/availability", response_model=DriverResponse)
def set_availability(
    driver_id: UUID,
    body: DriverAvailability,
    request: Request,
    current_user=Depends(require_permission("driver", "availability")),
    db=Depends(get_db),
):
    d = db.query(Driver).filter(Driver.id == str(driver_id)).first()
    if not d:
        raise HTTPException(404, "Driver not found")
    if not _driver_can_access(db, str(current_user.id), str(driver_id)):
        raise HTTPException(403, "Forbidden")
    if body.status not in ("AVAILABLE", "BUSY", "OFF_DUTY", "BREAK"):
        raise HTTPException(400, "Invalid status")
    old_status = d.status
    d.status = body.status
    d.last_availability_updated = datetime.utcnow()
    if body.location:
        d.current_location = {"lat": body.location.get("lat"), "lng": body.location.get("lng"), "updated_at": datetime.utcnow().isoformat()}
    db.commit()
    db.refresh(d)
    log_audit(db, current_user.id, "STATUS_CHANGE", "driver", d.id, {"status": old_status}, {"status": body.status}, request)
    return _driver_response(d, db)
