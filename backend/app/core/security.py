"""Security utilities: password hashing and JWT."""

import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (cost factor 12).
    
    Args:
        password: The plain text password to hash
    
    Returns:
        The hashed password string
    """
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def create_access_token(
    data: dict,
    secret_key: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token.
    
    Args:
        data: The payload data to encode in the token
        secret_key: The secret key to sign the token
        expires_delta: Optional custom expiration time
    
    Returns:
        The encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)
    
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def create_refresh_token(data: dict, secret_key: str) -> str:
    """Create a JWT refresh token with 7-day expiration.
    
    Args:
        data: The payload data to encode in the token
        secret_key: The secret key to sign the token
    
    Returns:
        The encoded JWT refresh token
    """
    return create_access_token(
        data,
        secret_key,
        expires_delta=timedelta(days=7),
    )


def decode_token(token: str, secret_key: str) -> Optional[dict]:
    """Decode and verify a JWT token.
    
    Args:
        token: The JWT token to decode
        secret_key: The secret key to verify the signature
    
    Returns:
        The decoded token payload, or None if invalid/expired
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
