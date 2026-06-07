import re

from pydantic import BaseModel, EmailStr, field_validator


def _validate_password_complexity(value: str) -> str:
    """Enforce password complexity rules."""
    errors = []
    if len(value) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", value):
        errors.append("at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        errors.append("at least one lowercase letter")
    if not re.search(r"\d", value):
        errors.append("at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append('at least one special character (!@#$%^&*(),.?":{}|<>)')
    if errors:
        raise ValueError("Password must contain: " + ", ".join(errors))
    return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return _validate_password_complexity(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str
