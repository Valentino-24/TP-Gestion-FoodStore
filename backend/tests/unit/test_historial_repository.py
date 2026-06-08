"""Tests for HistorialRepository — audit log for state transitions."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.pedidos.historial_repository import HistorialRepository
from app.models.historial_estado import HistorialEstado
from app.models.pedido import Pedido
from app.models.usuario import Usuario


@pytest.fixture
def repo(db_session: AsyncSession) -> HistorialRepository:
    return HistorialRepository(db_session)


async def _seed_estados(db_session: AsyncSession) -> None:
    """Idempotent seed of estado_pedido entries (ON CONFLICT DO NOTHING)."""
    raw_sql = text("""
        INSERT INTO estado_pedido (id, nombre, descripcion)
        VALUES
            (1, 'PENDIENTE', 'Esperando confirmacion'),
            (2, 'CONFIRMADO', 'Pago confirmado'),
            (6, 'CANCELADO', 'Cancelado')
        ON CONFLICT (id) DO NOTHING
    """)
    await db_session.execute(raw_sql)
    await db_session.flush()


async def _create_user(db_session: AsyncSession, user_id: int = 1) -> None:
    u = Usuario(
        id=user_id,
        nombre="Test",
        apellido="User",
        email=f"user{user_id}@test.com",
        password_hash="hash",
    )
    db_session.add(u)
    await db_session.flush()


async def _create_pedido(db_session: AsyncSession, user_id: int = 1) -> Pedido:
    await _seed_estados(db_session)
    p = Pedido(
        usuario_id=user_id,
        estado="PENDIENTE",
        total=100.0,
    )
    db_session.add(p)
    await db_session.flush()
    return p


class TestHistorialRepositoryCreate:
    async def test_create_returns_historial_with_id(self, repo, db_session):
        """GIVEN a HistorialEstado object WHEN create is called THEN it's persisted with an id."""
        await _create_user(db_session)
        pedido = await _create_pedido(db_session)

        historial = HistorialEstado(
            pedido_id=pedido.id,
            estado_hasta="PENDIENTE",
            observacion="Pedido creado",
        )
        result = await repo.create(historial)

        assert result.id is not None
        assert result.id > 0
        assert result.pedido_id == pedido.id
        assert result.estado_hasta == "PENDIENTE"
        assert result.observacion == "Pedido creado"

    async def test_create_with_full_data(self, repo, db_session):
        """GIVEN a HistorialEstado with all fields WHEN create is called THEN all fields are stored."""
        await _create_user(db_session, user_id=1)
        pedido = await _create_pedido(db_session)

        historial = HistorialEstado(
            pedido_id=pedido.id,
            estado_desde="PENDIENTE",
            estado_hasta="CONFIRMADO",
            usuario_id=1,
            observacion="Transición: PENDIENTE → CONFIRMADO",
        )
        result = await repo.create(historial)

        assert result.estado_desde == "PENDIENTE"
        assert result.estado_hasta == "CONFIRMADO"
        assert result.usuario_id == 1
        assert result.observacion == "Transición: PENDIENTE → CONFIRMADO"
        assert result.creado_en is not None


class TestHistorialRepositoryListByPedido:
    async def test_list_by_pedido_returns_in_insertion_order(self, repo, db_session):
        """GIVEN multiple historiales for a pedido WHEN list_by_pedido THEN entries are ordered chronologically."""
        await _create_user(db_session, user_id=1)
        pedido = await _create_pedido(db_session)

        h1 = HistorialEstado(
            pedido_id=pedido.id,
            estado_hasta="PENDIENTE",
            observacion="Pedido creado",
        )
        h2 = HistorialEstado(
            pedido_id=pedido.id,
            estado_desde="PENDIENTE",
            estado_hasta="CONFIRMADO",
            usuario_id=1,
            observacion="Transición: PENDIENTE → CONFIRMADO",
        )
        for h in (h1, h2):
            db_session.add(h)
        await db_session.flush()

        results = await repo.list_by_pedido(pedido.id)
        assert len(results) == 2
        # Entries returned in insertion order (creado_en asc via server_default)
        assert results[0].id < results[1].id
        assert results[0].estado_hasta == "PENDIENTE"
        assert results[1].estado_hasta == "CONFIRMADO"

    async def test_list_by_pedido_empty(self, repo, db_session):
        """GIVEN no historiales WHEN list_by_pedido THEN returns empty list."""
        results = await repo.list_by_pedido(99999)
        assert results == []

    async def test_list_by_pedido_respects_pedido_filter(self, repo, db_session):
        """GIVEN historiales for two different pedidos WHEN list_by_pedido THEN only matching ones."""
        await _create_user(db_session, user_id=1)
        p1 = await _create_pedido(db_session)
        p2 = await _create_pedido(db_session)

        h1 = HistorialEstado(pedido_id=p1.id, estado_hasta="PENDIENTE")
        h2 = HistorialEstado(pedido_id=p2.id, estado_hasta="PENDIENTE")
        db_session.add_all([h1, h2])
        await db_session.flush()

        results = await repo.list_by_pedido(p1.id)
        assert len(results) == 1
        assert results[0].pedido_id == p1.id
