"""RefreshTokens router — token refresh and logout endpoints."""

from fastapi import APIRouter, Depends, Request, Response, status

from app.auth.repository import UsuarioRepository
from app.auth.schemas import RefreshRequest, LogoutRequest, TokenResponse
from app.auth.service import AuthService
from app.config import settings
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


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rotate refresh token: invalidate old, issue new pair.

    Implements replay attack detection.
    """
    service = _get_auth_service(db)
    new_plain_token, old_record = await service.token_service.rotate_token(
        data.refresh_token
    )

    # Generate new access token for the same user
    from app.auth.repository import UsuarioRepository

    user_repo = UsuarioRepository(db)
    user = await user_repo.get_with_roles(old_record.user_id)

    from app.core.security import create_access_token
    from datetime import timedelta

    new_access = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": [role.nombre for role in user.roles],
        },
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_plain_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
)
async def logout(
    request: Request,
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """Revoke the provided refresh token.

    Idempotent: no error if token is already revoked or invalid.
    """
    service = _get_auth_service(db)
    await service.token_service.revoke_token(data.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
