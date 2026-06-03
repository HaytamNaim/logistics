"""Zones CRUD."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Zone
from app.core.rbac import get_current_user, require_permission
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from app.core.audit import log_audit
from fastapi import Request

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=list[ZoneResponse])
def list_zones(
    current_user=Depends(require_permission("order", "read")),
      db=Depends(get_db),
):
    return db.query(Zone).all()


@router.post("", response_model=ZoneResponse, status_code=201)
def create_zone(
    body: ZoneCreate,
    request: Request,
    current_user=Depends(require_permission("order", "create")),
      db=Depends(get_db),
):
    zone = Zone(**body.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    log_audit(db, current_user.id, "CREATE", "zone", zone.id, None, zone.__dict__, request)
    return zone


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: UUID,
    current_user=Depends(require_permission("order", "read")),
      db=Depends(get_db),
):
    z = db.query(Zone).filter(Zone.id == str(zone_id)).first()
    if not z:
        raise HTTPException(404, "Zone not found")
    return z


@router.patch("/{zone_id}", response_model=ZoneResponse)
def update_zone(
  zone_id: UUID,
  body: ZoneUpdate,
  request: Request,
  current_user=Depends(require_permission("order", "update")),
    db=Depends(get_db),
):
    z = db.query(Zone).filter(Zone.id == str(zone_id)).first()
    if not z:
        raise HTTPException(404, "Zone not found")
    old = {k: getattr(z, k) for k in ("name", "polygon", "parent_zone_id")}
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(z, k, v)
    db.commit()
    db.refresh(z)
    log_audit(db, current_user.id, "UPDATE", "zone", z.id, old, {k: getattr(z, k) for k in old}, request)
    return z
