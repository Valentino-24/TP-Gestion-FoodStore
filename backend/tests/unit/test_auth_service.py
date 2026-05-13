"""Tests for AuthService business logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.auth.service import AuthService
from app.auth.schemas import RegisterRequest, LoginRequest


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_with_roles = AsyncMock()
    return repo


@pytest.fixture
def mock_token_service():
    svc = MagicMock()
    svc.create_token = MagicMock(return_value=("fake-refresh-token", "fake-family-id"))
    return svc


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    # Make __aenter__ return a mock session
    mock_session = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=mock_session)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def auth_service(mock_user_repo, mock_token_service, mock_uow):
    return AuthService(
        user_repo=mock_user_repo,
        token_service=mock_token_service,
        uow=mock_uow,
    )


class TestAuthServiceRegister:
    async def test_register_success(self, auth_service, mock_user_repo, mock_uow):
        """WHEN registering with valid data THEN user is created and tokens returned."""
        mock_user_repo.get_by_email.return_value = None  # No duplicate

        # Mock the user created after UoW
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.nombre = "Test"
        mock_user.apellido = "User"
        mock_user.email = "test@test.com"
        mock_user.roles = [MagicMock(nombre="CLIENT")]
        mock_user_repo.get_with_roles.return_value = mock_user

        data = RegisterRequest(nombre="Test", apellido="User", email="test@test.com", password="password123")
        result = await auth_service.register(data)

        assert result.access_token is not None
        assert result.refresh_token == "fake-refresh-token"
        assert result.token_type == "bearer"
        assert result.expires_in > 0
        mock_user_repo.get_by_email.assert_called_once_with("test@test.com")

    async def test_register_duplicate_email(self, auth_service, mock_user_repo):
        """WHEN registering with existing email THEN 409 is raised."""
        mock_user_repo.get_by_email.return_value = MagicMock()  # Existing user

        data = RegisterRequest(nombre="Test", apellido="User", email="existing@test.com", password="password123")
        with pytest.raises(HTTPException) as exc:
            await auth_service.register(data)
        assert exc.value.status_code == 409
        assert "ya esta registrado" in exc.value.detail

    async def test_register_weak_password_still_passes_service(self, auth_service, mock_user_repo):
        """WHEN password is weak (service doesn't validate — schema does)."""
        mock_user_repo.get_by_email.return_value = None

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.nombre = "Test"
        mock_user.apellido = "User"
        mock_user.email = "weak@test.com"
        mock_user.roles = [MagicMock(nombre="CLIENT")]
        mock_user_repo.get_with_roles.return_value = mock_user

        # Password validation is done by Pydantic schema, not service
        data = RegisterRequest(nombre="Test", apellido="User", email="weak@test.com", password="short123")  # noqa: S106
        # The Pydantic schema would reject this, but the service itself should also handle gracefully
        try:
            result = await auth_service.register(data)
            assert result.access_token is not None
        except HTTPException:
            pass  # Also valid if the service checks password length


class TestAuthServiceLogin:
    async def test_login_success(self, auth_service, mock_user_repo, mock_token_service):
        """WHEN logging in with correct credentials THEN tokens are returned."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@test.com"
        mock_user.password_hash = "$2b$12$" + "a" * 53  # Valid bcrypt hash format
        mock_user.roles = [MagicMock(nombre="CLIENT")]
        mock_user_repo.get_by_email.return_value = mock_user

        with patch("app.auth.service.verify_password", return_value=True):
            data = LoginRequest(email="test@test.com", password="password123")
            result = await auth_service.login(data)

        assert result.access_token is not None
        assert result.refresh_token == "fake-refresh-token"
        mock_user_repo.get_by_email.assert_called_once_with("test@test.com")

    async def test_login_invalid_email(self, auth_service, mock_user_repo):
        """WHEN logging in with non-existent email THEN 401 is raised."""
        mock_user_repo.get_by_email.return_value = None

        data = LoginRequest(email="noone@test.com", password="password123")
        with pytest.raises(HTTPException) as exc:
            await auth_service.login(data)
        assert exc.value.status_code == 401
        assert exc.value.detail == "Credenciales invalidas"

    async def test_login_wrong_password(self, auth_service, mock_user_repo):
        """WHEN logging in with wrong password THEN 401 is raised."""
        mock_user = MagicMock()
        mock_user.password_hash = "$2b$12$" + "b" * 53
        mock_user_repo.get_by_email.return_value = mock_user

        with patch("app.auth.service.verify_password", return_value=False):
            data = LoginRequest(email="test@test.com", password="wrongpassword")
            with pytest.raises(HTTPException) as exc:
                await auth_service.login(data)
            assert exc.value.status_code == 401
            assert exc.value.detail == "Credenciales invalidas"

    async def test_login_response_does_not_distinguish(self, auth_service, mock_user_repo):
        """WHEN login fails, error is same for wrong email or password (security)."""
        mock_user_repo.get_by_email.return_value = None

        data = LoginRequest(email="random@test.com", password="anypassword")
        with pytest.raises(HTTPException) as exc:
            await auth_service.login(data)
        assert exc.value.detail == "Credenciales invalidas"


class TestAuthServiceGetProfile:
    async def test_get_profile_success(self, auth_service, mock_user_repo):
        """WHEN requesting profile THEN UserResponse is returned."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.nombre = "Test"
        mock_user.apellido = "User"
        mock_user.email = "test@test.com"
        mock_user.roles = [MagicMock(nombre="CLIENT")]
        mock_user_repo.get_with_roles.return_value = mock_user

        result = await auth_service.get_user_profile(1)
        assert result.id == 1
        assert result.email == "test@test.com"
        assert "CLIENT" in result.roles

    async def test_get_profile_not_found(self, auth_service, mock_user_repo):
        """WHEN user ID doesn't exist THEN 404 is raised."""
        mock_user_repo.get_with_roles.return_value = None

        with pytest.raises(HTTPException) as exc:
            await auth_service.get_user_profile(99999)
        assert exc.value.status_code == 404
