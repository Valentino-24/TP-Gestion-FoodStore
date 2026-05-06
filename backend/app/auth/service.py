"""Auth service — registration, login, and user profile."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status

from app.auth.repository import UsuarioRepository
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.usuario_rol import UsuarioRol
from app.refreshtokens.service import RefreshTokenService
from app.unit_of_work import UnitOfWork

# Fixed role ID for new registrations
CLIENT_ROLE_ID = 4

# Generic error message (security: don't reveal whether email exists)
GENERIC_CREDENTIALS_ERROR = "Credenciales invalidas"


class AuthService:
    """Handles authentication business logic."""

    def __init__(
        self,
        user_repo: UsuarioRepository,
        token_service: RefreshTokenService,
        uow: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.token_service = token_service
        self.uow = uow

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user with automatic CLIENT role assignment.

        Args:
            data: Registration request with name, email, password.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            HTTPException 409 if email already registered.
        """
        # Check for duplicate email
        existing = await self.user_repo.get_by_email(data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya esta registrado",
            )

        # Hash password in service layer (D4)
        password_hash = get_password_hash(data.password)

        # Create user and assign CLIENT role within UoW
        from app.models.usuario import Usuario

        async with self.uow as session:
            user = Usuario(
                nombre=data.nombre,
                apellido=data.apellido,
                email=data.email,
                password_hash=password_hash,
            )
            session.add(user)
            await session.flush()  # Get user.id

            # Assign CLIENT role
            user_role = UsuarioRol(usuario_id=user.id, rol_id=CLIENT_ROLE_ID)
            session.add(user_role)

        # Generate tokens after commit
        return self._generate_token_pair(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return token pair.

        Args:
            data: Login request with email and password.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            HTTPException 401 with generic message for any failure.
        """
        # Look up user by email
        user = await self.user_repo.get_by_email(data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=GENERIC_CREDENTIALS_ERROR,
            )

        # Verify password
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=GENERIC_CREDENTIALS_ERROR,
            )

        return self._generate_token_pair(user)

    async def get_user_profile(self, user_id: int) -> UserResponse:
        """Get user profile with roles.

        Args:
            user_id: The authenticated user's ID.

        Returns:
            UserResponse with profile data and role names.

        Raises:
            HTTPException 404 if user not found.
        """
        user = await self.user_repo.get_with_roles(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return UserResponse(
            id=user.id,
            nombre=user.nombre,
            apellido=user.apellido,
            email=user.email,
            roles=[role.nombre for role in user.roles],
        )

    def _generate_token_pair(self, user) -> TokenResponse:
        """Create access JWT and opaque refresh token for a user.

        Args:
            user: Usuario object with roles loaded.

        Returns:
            TokenResponse with both tokens.
        """
        # Access token with required claims
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "roles": [role.nombre for role in user.roles],
            },
            secret_key=settings.SECRET_KEY,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        # Opaque refresh token (stored as SHA-256 hash in BD)
        plain_refresh, _ = self.token_service.create_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=plain_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
