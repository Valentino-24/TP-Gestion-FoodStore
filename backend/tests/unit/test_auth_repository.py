"""Tests for AuthRepository (UsuarioRepository) custom queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import UsuarioRepository
from app.models.usuario import Usuario
from app.core.security import get_password_hash


@pytest.fixture
def repo(db_session: AsyncSession) -> UsuarioRepository:
    return UsuarioRepository(db_session)


class TestUsuarioRepositoryGetByEmail:
    async def test_get_by_email_found(self, repo, db_session):
        """WHEN searching by existing email THEN user is returned."""
        user = Usuario(
            nombre="Test", apellido="User", email="findme@test.com",
            password_hash=get_password_hash("password123"),
        )
        db_session.add(user)
        await db_session.flush()
        found = await repo.get_by_email("findme@test.com")
        assert found is not None
        assert found.email == "findme@test.com"

    async def test_get_by_email_not_found(self, repo):
        """WHEN searching by non-existent email THEN None is returned."""
        found = await repo.get_by_email("nonexistent@test.com")
        assert found is None

    async def test_get_by_email_excludes_soft_deleted(self, repo, db_session):
        """WHEN user is soft-deleted THEN get_by_email returns None."""
        from datetime import datetime, timezone
        user = Usuario(
            nombre="Deleted", apellido="User", email="deleted@test.com",
            password_hash=get_password_hash("password123"),
            eliminado_en=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        found = await repo.get_by_email("deleted@test.com")
        assert found is None

    async def test_get_by_email_includes_roles(self, repo, db_session):
        """WHEN getting by email THEN roles are eagerly loaded."""
        from app.models.rol import Rol

        role = Rol(id=4, nombre="CLIENT", descripcion="Client role")
        db_session.add(role)
        await db_session.flush()

        user = Usuario(
            nombre="Role", apellido="Test", email="role@test.com",
            password_hash=get_password_hash("password123"),
        )
        db_session.add(user)
        await db_session.flush()

        from app.models.usuario_rol import UsuarioRol
        ur = UsuarioRol(usuario_id=user.id, rol_id=4)
        db_session.add(ur)
        await db_session.flush()

        found = await repo.get_by_email("role@test.com")
        assert found is not None
        assert len(found.roles) > 0
        assert found.roles[0].nombre == "CLIENT"


class TestUsuarioRepositoryGetWithRoles:
    async def test_get_with_roles_returns_roles(self, repo, db_session):
        """WHEN getting user with roles THEN roles are eagerly loaded."""
        from app.models.rol import Rol
        role = Rol(id=4, nombre="CLIENT", descripcion="Client")
        db_session.add(role)
        await db_session.flush()

        user = Usuario(
            nombre="WithRoles", apellido="Test", email="roles2@test.com",
            password_hash=get_password_hash("password123"),
        )
        db_session.add(user)
        await db_session.flush()

        from app.models.usuario_rol import UsuarioRol
        db_session.add(UsuarioRol(usuario_id=user.id, rol_id=4))

        found = await repo.get_with_roles(user.id)
        assert found is not None
        assert len(found.roles) > 0
        assert found.roles[0].nombre == "CLIENT"
