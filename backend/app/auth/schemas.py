"""Auth schemas — request/response models with validation."""

import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# Email regex: RFC 5322 simplified
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_password(password: str) -> str:
    """Validate password meets minimum requirements."""
    if len(password) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres")
    return password


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    nombre: str
    apellido: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        return validate_password(v)


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response with authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """Response with user profile data."""

    id: int
    nombre: str
    apellido: str
    email: str
    roles: list[str]


class RefreshRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for logout."""

    refresh_token: str
