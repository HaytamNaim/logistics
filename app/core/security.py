"""JWT and password hashing."""
from datetime import datetime, timedelta
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(sub: str, roles: list[str], scope_zone_id: str | None = None) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload: dict[str, Any] = {"sub": sub, "exp": expire, "iat": now, "type": "access"}
    if roles:
        payload["roles"] = roles
    if scope_zone_id:
        payload["scope_zone_id"] = scope_zone_id
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(sub: str) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.jwt_refresh_expire_days)
    return jwt.encode(
        {"sub": sub, "exp": expire, "iat": now, "type": "refresh"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
