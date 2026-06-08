"""Auth router — registration, login, and user profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.repository import UsuarioRepository
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.core.cookies import set_auth_cookies
from app.database import AsyncSession, get_db
from app.dependencies import CurrentUser
from app.refreshtokens.repository import RefreshTokenRepository
from app.refreshtokens.service import RefreshTokenService
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limiter for login endpoint
limiter = Limiter(key_func=get_remote_address)


def _get_auth_service(db: AsyncSession) -> AuthService:
    """Construct AuthService with its dependencies."""
    user_repo = UsuarioRepository(db)
    token_repo = RefreshTokenRepository(db)
    token_service = RefreshTokenService(token_repo)
    uow = UnitOfWork()
    return AuthService(user_repo, token_service, uow)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: Request,
    data: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with automatic CLIENT role assignment.

    Returns access and refresh tokens on success.
    Tokens are also set as httpOnly cookies for automatic inclusion.
    """
    service = _get_auth_service(db)
    tokens = await service.register(data)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
)
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password.

    Returns a generic error for invalid credentials (security).
    Rate limited: 5 attempts per IP per 15 minutes.
    Tokens are also set as httpOnly cookies for automatic inclusion.
    """
    service = _get_auth_service(db)
    tokens = await service.login(data)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user's profile with roles."""
    service = _get_auth_service(db)
    return await service.get_user_profile(current_user.id)
