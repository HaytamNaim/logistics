"""POST /auth/login, POST /auth/token, POST /auth/refresh."""
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.limiter import limiter
from app.models import User, UserRole, Role
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.rbac import get_user_roles
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest

logger = logging.getLogger(__name__)

# In-memory account lockout store.
# NOTE: This only works for single-instance deployments.
# For multi-instance / horizontally-scaled setups, replace with a shared
# Redis store (e.g. using redis-py with INCR + EXPIRE).
_failed_attempts: dict[str, list[float]] = {}  # email -> list of failure timestamps
MAX_FAILURES = 5
LOCKOUT_SECONDS = 900  # 15 minutes


def _prune_failures(email: str) -> None:
    """Remove failure timestamps older than the lockout window."""
    cutoff = time.time() - LOCKOUT_SECONDS
    _failed_attempts[email] = [t for t in _failed_attempts.get(email, []) if t > cutoff]


def _is_locked_out(email: str) -> bool:
    _prune_failures(email)
    return len(_failed_attempts.get(email, [])) >= MAX_FAILURES


def _record_failure(email: str) -> None:
    _failed_attempts.setdefault(email, []).append(time.time())
    _prune_failures(email)


def _clear_failures(email: str) -> None:
    _failed_attempts.pop(email, None)


router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens_for_user(user, db) -> TokenResponse:
    roles_with_scope = get_user_roles(db, str(user.id))
    role_codes = [r[0] for r in roles_with_scope]
    scope_zone_id = roles_with_scope[0][1] if roles_with_scope else None
    access_token = create_access_token(str(user.id), role_codes, scope_zone_id)
    refresh_token = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
def token(request: Request, form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """OAuth2-compatible token endpoint (username=email, password=password)."""
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return _issue_tokens_for_user(user, db)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db=Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    email = body.email

    if _is_locked_out(email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(body.password, user.password_hash):
        logger.warning("Failed login attempt for email=%s from ip=%s", email, client_ip)
        _record_failure(email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

    _clear_failures(email)
    logger.info("Successful login for user_id=%s from ip=%s", user.id, client_ip)
    return _issue_tokens_for_user(user, db)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
def refresh(request: Request, body: RefreshRequest, db=Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        logger.warning("Invalid refresh token from ip=%s", client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    sub = payload.get("sub")
    if not sub:
        logger.warning("Invalid refresh token from ip=%s", client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == sub, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    roles_with_scope = get_user_roles(db, str(user.id))
    role_codes = [r[0] for r in roles_with_scope]
    scope_zone_id = roles_with_scope[0][1] if roles_with_scope else None
    access_token = create_access_token(str(user.id), role_codes, scope_zone_id)
    return TokenResponse(access_token=access_token, refresh_token=body.refresh_token)
