"""RefreshTokens router — token refresh and logout endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth.repository import UsuarioRepository
from app.auth.schemas import RefreshRequest, LogoutRequest, TokenResponse
from app.auth.service import AuthService
from app.config import settings
from app.core.cookies import (
    REFRESH_TOKEN_COOKIE,
    clear_auth_cookies,
    set_auth_cookies,
)
from app.core.security import create_access_token
from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser
from app.refreshtokens.repository import RefreshTokenRepository
from app.refreshtokens.service import RefreshTokenService
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(db: AsyncSession) -> AuthService:
    """Construct AuthService with its dependencies."""
    user_repo = UsuarioRepository(db)
    token_repo = RefreshTokenRepository(db)
    token_service = RefreshTokenService(token_repo)
    uow = UnitOfWork()
    return AuthService(user_repo, token_service, uow)


async def _get_refresh_token(request: Request) -> str:
    """Extract refresh token from cookie or request body.

    Priority: httpOnly cookie > request body (legacy).
    """
    token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not token:
        # Legacy: read from body
        import json

        try:
            body = json.loads(await request.body())
            token = body.get("refresh_token", "")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token no proporcionado",
            )
    return token


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Rotate refresh token: invalidate old, issue new pair.

    Reads the refresh token from the httpOnly cookie (or legacy body).
    Sets new cookies on success.
    Implements replay attack detection.
    """
    refresh_token_value = await _get_refresh_token(request)

    service = _get_auth_service(db)
    new_plain_token, old_record = await service.token_service.rotate_token(
        refresh_token_value
    )

    # Generate new access token for the same user
    user_repo = UsuarioRepository(db)
    user = await user_repo.get_with_roles(old_record.user_id)

    new_access = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": [role.nombre for role in user.roles],
        },
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    tokens = TokenResponse(
        access_token=new_access,
        refresh_token=new_plain_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # Set new auth cookies
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Revoke the refresh token and clear auth cookies.

    Reads the refresh token from the httpOnly cookie (or legacy body).
    Idempotent: no error if token is already revoked or invalid.
    """
    try:
        refresh_token_value = await _get_refresh_token(request)
        if refresh_token_value:
            service = _get_auth_service(db)
            await service.token_service.revoke_token(refresh_token_value)
    except HTTPException:
        pass  # No token to revoke — still clear cookies

    clear_auth_cookies(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
