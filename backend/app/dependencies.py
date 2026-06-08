"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated, AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.cookies import ACCESS_TOKEN_COOKIE
from app.database import AsyncSession, async_session_maker, get_db
from app.models.usuario import Usuario


# OAuth2 scheme (kept for backward compatibility during transition)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Resolve the authenticated user from the request.

    Token resolution order:
      1. httpOnly cookie ``access_token``
      2. ``Authorization: Bearer <token>`` header (legacy)

    Args:
        request: Incoming request (used to read cookies + fallback header).
        db: Database session.

    Returns:
        Usuario object with roles loaded.

    Raises:
        HTTPException 401 if no valid token is found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Try httpOnly cookie first
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)

    # 2. Fallback: Authorization header (legacy / Swagger UI)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise credentials_exception

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
