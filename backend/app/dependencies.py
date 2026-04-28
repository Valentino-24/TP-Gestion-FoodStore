"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings
from app.database import AsyncSession


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    from app.database import async_session_maker
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Type alias for database session
DBSession = Annotated[AsyncSession, Depends(get_db)]


# Current user dependency (placeholder - will be implemented in auth-system)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
):
    """Dependency to get the current authenticated user.
    
    This is a placeholder. Full implementation in auth-system change.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object (placeholder - type to be defined)
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # TODO: Implement actual user lookup when Usuario model exists
    # For now, return placeholder
    return {"id": user_id, "email": "placeholder@email.com"}


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(allowed_roles: list[str]):
    """Dependency factory for role-based access control.
    
    Args:
        allowed_roles: List of role names that are allowed
        
    Returns:
        Dependency function that checks user role
        
    Example:
        @router.get("/admin")
        async def admin_only(user: CurrentUser = Depends(require_role(["ADMIN"]))):
            ...
    """
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        # TODO: Implement actual role check when Usuario and UsuarioRol models exist
        # For now, allow all authenticated users
        return current_user
    
    return role_checker