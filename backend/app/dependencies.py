"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import AsyncSession, async_session_maker, get_db
from app.models.usuario import Usuario


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Decode JWT and return the authenticated user with roles.

    Args:
        token: JWT token from Authorization header.
        db: Database session.

    Returns:
        Usuario object with roles loaded.

    Raises:
        HTTPException 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Look up user with roles
    stmt = (
        select(Usuario)
        .where(Usuario.id == int(user_id), Usuario.eliminado_en.is_(None))
        .options(selectinload(Usuario.roles))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


# Type alias for authenticated user dependency
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_role(allowed_roles: list[str]):
    """Dependency factory for role-based access control.

    Args:
        allowed_roles: List of role names that are allowed access.

    Returns:
        Dependency function that checks user roles.

    Raises:
        HTTPException 403 if user lacks required roles.

    Example:
        @router.get("/admin")
        async def admin_only(user: CurrentUser = Depends(require_role(["ADMIN"]))):
            ...
    """
    async def role_checker(current_user: CurrentUser):
        user_role_names = [role.nombre for role in current_user.roles]
        if not any(role in user_role_names for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso",
            )
        return current_user

    return role_checker
