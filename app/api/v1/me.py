"""GET /me — current user + roles."""
from fastapi import APIRouter, Depends
from app.database import SessionLocal
from app.models import User
from app.core.rbac import get_current_user, get_user_roles
from app.schemas.user import UserMe

router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        roles_with_scope = get_user_roles(db, str(current_user.id))
        roles = [{"code": r[0], "scope_zone_id": r[1]} for r in roles_with_scope]
        return UserMe(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            roles=roles,
        )
    finally:
        db.close()
