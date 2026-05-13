"""Tests for PedidoRepository custom queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.pedidos.repository import PedidoRepository
from app.models.pedido import Pedido
from app.models.usuario import Usuario
from datetime import datetime


@pytest.fixture
def repo(db_session: AsyncSession) -> PedidoRepository:
    return PedidoRepository(db_session)


async def _create_user(db_session: AsyncSession, user_id: int) -> None:
    """Helper to create a minimal user for FK constraints."""
    u = Usuario(
        id=user_id,
        nombre=f"User{user_id}",
        apellido="Test",
        email=f"user{user_id}@test.com",
        password_hash="hash",
    )
    db_session.add(u)
    await db_session.flush()


class TestPedidoRepositoryGetByCliente:
    async def test_get_by_cliente_id(self, repo, db_session):
        """WHEN getting pedidos by cliente_id THEN only their orders are returned."""
        await _create_user(db_session, 1)
        await _create_user(db_session, 2)
        p1 = Pedido(usuario_id=1, cliente_id=1, total=100.0, estado="pendiente", fecha_creacion=datetime.utcnow())
        p2 = Pedido(usuario_id=2, cliente_id=2, total=200.0, estado="pendiente", fecha_creacion=datetime.utcnow())
        p3 = Pedido(usuario_id=1, cliente_id=1, total=150.0, estado="confirmado", fecha_creacion=datetime.utcnow())
        db_session.add_all([p1, p2, p3])
        await db_session.flush()
        results = await repo.get_by_cliente_id(1)
        assert len(results) == 2
        assert all(r.cliente_id == 1 for r in results)


class TestPedidoRepositoryGetAll:
    async def test_get_all(self, repo, db_session):
        """WHEN getting all pedidos THEN they are ordered by creation date desc."""
        from datetime import timedelta
        await _create_user(db_session, 1)
        await _create_user(db_session, 2)
        now = datetime.utcnow()
        p1 = Pedido(usuario_id=1, cliente_id=1, total=100.0, estado="pendiente", fecha_creacion=now - timedelta(hours=2))
        p2 = Pedido(usuario_id=2, cliente_id=2, total=200.0, estado="pendiente", fecha_creacion=now)
        db_session.add_all([p1, p2])
        await db_session.flush()
        results = await repo.get_all()
        # Most recent first
        assert len(results) == 2
        # p2 (newer) should be first when ordered by fecha_creacion desc


class TestPedidoRepositoryGetById:
    async def test_get_by_id_found(self, repo, db_session):
        """WHEN getting pedido by existing ID THEN it is returned."""
        await _create_user(db_session, 1)
        p = Pedido(usuario_id=1, cliente_id=1, total=99.99, estado="pendiente", fecha_creacion=datetime.utcnow())
        db_session.add(p)
        await db_session.flush()
        found = await repo.get_by_id(p.id)
        assert found is not None
        assert found.total == 99.99

    async def test_get_by_id_not_found(self, repo):
        """WHEN getting pedido by non-existent ID THEN None."""
        found = await repo.get_by_id(99999)
        assert found is None
