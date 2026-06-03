"""Role-Based Access Control — permissions and get_current_user."""
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, Role
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

# (resource_type, action) -> roles that may perform it
PERMISSIONS = {
    ("order", "read"): ["ADMIN", "FLEET_MANAGER", "DRIVER"],
    ("order", "create"): ["ADMIN", "FLEET_MANAGER"],
    ("order", "update"): ["ADMIN", "FLEET_MANAGER"],
    ("order", "delete"): ["ADMIN"],
    ("order", "transition"): ["ADMIN", "FLEET_MANAGER"],
    ("delivery", "read"): ["ADMIN", "FLEET_MANAGER", "DRIVER"],
    ("delivery", "create"): ["ADMIN", "FLEET_MANAGER"],
    ("delivery", "update"): ["ADMIN", "FLEET_MANAGER"],
    ("delivery", "status"): ["FLEET_MANAGER", "DRIVER"],
    ("delivery", "assign"): ["ADMIN", "FLEET_MANAGER"],
    ("delivery", "assign_auto"): ["ADMIN", "FLEET_MANAGER"],
    ("driver", "read"): ["ADMIN", "FLEET_MANAGER", "DRIVER"],
    ("driver", "update"): ["ADMIN", "FLEET_MANAGER"],
    ("driver", "availability"): ["FLEET_MANAGER", "DRIVER"],
    ("route", "read"): ["ADMIN", "FLEET_MANAGER", "DRIVER"],
    ("route", "create"): ["FLEET_MANAGER"],
    ("route", "update"): ["FLEET_MANAGER"],
    ("route", "optimize"): ["FLEET_MANAGER"],
    ("route", "publish"): ["FLEET_MANAGER"],
    ("analytics", "read"): ["ADMIN", "FLEET_MANAGER"],
    ("audit", "read"): ["ADMIN"],
}


def get_optional_user(
    db=Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> User | None:
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    user = db.query(User).filter(User.id == sub, User.is_active.is_(True)).first()
    return user


def get_current_user(
    user: User | None = Depends(get_optional_user),
) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_user_roles(db: Session, user_id: str) -> list[tuple[str, str | None]]:
    """Return list of (role_code, scope_zone_id)."""
    rows = (
        db.query(Role.code, UserRole.scope_zone_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [(r.code, str(r.scope_zone_id) if r.scope_zone_id else None) for r in rows]


def require_permission(resource_type: str, action: str):
    """Dependency factory: require (resource_type, action) for current user."""

    def _check(
        current_user: User = Depends(get_current_user),
        db=Depends(get_db),
    ) -> User:
        roles_with_scope = get_user_roles(db, str(current_user.id))
        allowed_roles = PERMISSIONS.get((resource_type, action), [])
        if not allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission not defined")
        role_codes = [r[0] for r in roles_with_scope]
        if not any(r in allowed_roles for r in role_codes):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return _check


def require_roles(*role_codes: str):
    """Dependency: require at least one of the given roles."""

    def _check(
        current_user: User = Depends(get_current_user),
        db=Depends(get_db),
    ) -> User:
        roles_with_scope = get_user_roles(db, str(current_user.id))
        role_codes_set = set(role_codes)
        if not any(r[0] in role_codes_set for r in roles_with_scope):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _check
