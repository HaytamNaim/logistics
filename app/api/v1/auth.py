"""POST /auth/login, POST /auth/token, POST /auth/refresh, POST /auth/logout."""
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
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
from app.config import get_settings

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
settings = get_settings()

# Cookie max-age values derived from the JWT settings
_ACCESS_MAX_AGE = settings.jwt_access_expire_minutes * 60  # seconds
_REFRESH_MAX_AGE = settings.jwt_refresh_expire_days * 24 * 60 * 60  # seconds


def _issue_tokens_for_user(user, db) -> tuple[str, str]:
    """Return (access_token, refresh_token) strings."""
    roles_with_scope = get_user_roles(db, str(user.id))
    role_codes = [r[0] for r in roles_with_scope]
    scope_zone_id = roles_with_scope[0][1] if roles_with_scope else None
    access_token = create_access_token(str(user.id), role_codes, scope_zone_id)
    refresh_token = create_refresh_token(str(user.id))
    return access_token, refresh_token


def _build_token_response(access_token: str, refresh_token: str) -> JSONResponse:
    """Build a JSONResponse that also sets HttpOnly token cookies."""
    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_ACCESS_MAX_AGE,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_REFRESH_MAX_AGE,
        path="/api/v1/auth/refresh",
    )
    return response


@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")
def token(request: Request, form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """OAuth2-compatible token endpoint (username=email, password=password)."""
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    access_token, refresh_token = _issue_tokens_for_user(user, db)
    return _build_token_response(access_token, refresh_token)


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
    access_token, refresh_token = _issue_tokens_for_user(user, db)
    return _build_token_response(access_token, refresh_token)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
def refresh(request: Request, body: RefreshRequest, db=Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    # Accept refresh token from request body or cookie fallback
    refresh_token_value = body.refresh_token
    if not refresh_token_value:
        refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    payload = decode_token(refresh_token_value)
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

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "token_type": "bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_ACCESS_MAX_AGE,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return response
