"""Tests for ClienteRepository custom queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.clientes.repository import ClienteRepository
from app.models.cliente import Cliente


@pytest.fixture
def repo(db_session: AsyncSession) -> ClienteRepository:
    return ClienteRepository(db_session)


class TestClienteRepositoryGetByEmail:
    async def test_get_by_email_found(self, repo, db_session):
        """WHEN searching by existing email THEN customer is returned."""
        cli = Cliente(
            nombre="Juan", apellido="Perez", email="juan@test.com",
            telefono="123", direccion="Calle",
        )
        db_session.add(cli)
        await db_session.flush()
        found = await repo.get_by_email("juan@test.com")
        assert found is not None
        assert found.email == "juan@test.com"

    async def test_get_by_email_not_found(self, repo):
        """WHEN searching by non-existent email THEN None is returned."""
        found = await repo.get_by_email("no@test.com")
        assert found is None


class TestClienteRepositoryGetActive:
    async def test_get_active_only_active(self, repo, db_session):
        """WHEN getting active customers THEN only active ones are returned."""
        c1 = Cliente(nombre="A1", apellido="U1", email="a1@test.com", activo=True)
        c2 = Cliente(nombre="A2", apellido="U2", email="a2@test.com", activo=False)
        db_session.add_all([c1, c2])
        await db_session.flush()
        active = await repo.get_active()
        assert len(active) == 1
        assert active[0].email == "a1@test.com"

    async def test_get_active_pagination(self, repo, db_session):
        """WHEN paginating active customers THEN correct pages."""
        for i in range(5):
            db_session.add(Cliente(
                nombre=f"Client{i}", apellido="T", email=f"c{i}@test.com",
                activo=True,
            ))
        await db_session.flush()
        page1 = await repo.get_active(skip=0, limit=2)
        page2 = await repo.get_active(skip=2, limit=2)
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id


class TestClienteRepositoryCountActive:
    async def test_count_active(self, repo, db_session):
        """WHEN counting active customers THEN correct count."""
        db_session.add_all([
            Cliente(nombre="C1", apellido="U1", email="c1@test.com", activo=True),
            Cliente(nombre="C2", apellido="U2", email="c2@test.com", activo=True),
            Cliente(nombre="C3", apellido="U3", email="c3@test.com", activo=False),
        ])
        await db_session.flush()
        count = await repo.count_active()
        assert count == 2
