"""Tests for stock management — decrement_stock and restore_stock in PedidoService."""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.pedidos.service import PedidoService
from app.pedidos.repository import PedidoRepository


@pytest.fixture
def service(db_session: AsyncSession) -> PedidoService:
    repo = PedidoRepository(db_session)
    return PedidoService(repo, db_session)


async def _create_category(db_session: AsyncSession) -> int:
    from app.models.categoria import Categoria
    cat = Categoria(nombre="Test Cat", descripcion="Test")
    db_session.add(cat)
    await db_session.flush()
    return cat.id


async def _create_product(
    db_session: AsyncSession, cat_id: int, stock: int | None = 10, precio: float = 50.0
) -> int:
    from app.models.producto import Producto
    prod = Producto(
        nombre="Test Product",
        descripcion="Test",
        precio=precio,
        categoria_id=cat_id,
        activo=True,
        stock_cantidad=stock,
    )
    db_session.add(prod)
    await db_session.flush()
    return prod.id


class TestDecrementStock:
    async def test_decrements_stock_when_sufficient(self, service, db_session):
        """GIVEN a product with stock=10 WHEN decrement_stock(5) THEN stock becomes 5."""
        cat_id = await _create_category(db_session)
        prod_id = await _create_product(db_session, cat_id, stock=10)

        await service._decrement_stock(prod_id, 5)

        from app.models.producto import Producto
        from sqlalchemy import select
        result = await db_session.execute(select(Producto).where(Producto.id == prod_id))
        prod = result.scalar_one()
        assert prod.stock_cantidad == 5

    async def test_raises_400_when_insufficient_stock(self, service, db_session):
        """GIVEN a product with stock=3 WHEN decrement_stock(10) THEN raises 400."""
        cat_id = await _create_category(db_session)
        prod_id = await _create_product(db_session, cat_id, stock=3)

        with pytest.raises(HTTPException) as exc:
            await service._decrement_stock(prod_id, 10)
        assert exc.value.status_code == 400
        assert "Stock insuficiente" in str(exc.value.detail)

    async def test_raises_404_when_product_not_found(self, service, db_session):
        """GIVEN a non-existent product WHEN decrement_stock THEN raises 404."""
        with pytest.raises(HTTPException) as exc:
            await service._decrement_stock(99999, 1)
        assert exc.value.status_code == 404
        assert "no encontrado" in str(exc.value.detail)

    async def test_decrements_exactly_to_zero(self, service, db_session):
        """GIVEN a product with stock=1 WHEN decrement_stock(1) THEN stock becomes 0."""
        cat_id = await _create_category(db_session)
        prod_id = await _create_product(db_session, cat_id, stock=1)

        await service._decrement_stock(prod_id, 1)

        from app.models.producto import Producto
        from sqlalchemy import select
        result = await db_session.execute(select(Producto).where(Producto.id == prod_id))
        prod = result.scalar_one()
        assert prod.stock_cantidad == 0

    async def test_decrement_raises_400_when_stock_is_zero(self, service, db_session):
        """GIVEN a product with stock=0 WHEN decrement_stock(1) THEN raises 400 (insufficient)."""
        cat_id = await _create_category(db_session)
        prod_id = await _create_product(db_session, cat_id, stock=0)

        with pytest.raises(HTTPException) as exc:
            await service._decrement_stock(prod_id, 1)
        assert exc.value.status_code == 400
        assert "Stock insuficiente" in str(exc.value.detail)


class TestRestoreStock:
    async def test_restores_stock_after_decrement(self, service, db_session):
        """GIVEN a product decremented from 10 to 5 WHEN restore_stock(5) THEN stock becomes 10."""
        cat_id = await _create_category(db_session)
        prod_id = await _create_product(db_session, cat_id, stock=10)

        await service._decrement_stock(prod_id, 5)
        await service._restore_stock(prod_id, 5)

        from app.models.producto import Producto
        from sqlalchemy import select
        result = await db_session.execute(select(Producto).where(Producto.id == prod_id))
        prod = result.scalar_one()
        assert prod.stock_cantidad == 10

    async def test_restore_noop_when_product_missing(self, service, db_session):
        """GIVEN a non-existent product WHEN restore_stock THEN no-op (no raise)."""
        await service._restore_stock(99999, 5)

    async def test_does_not_raise_on_missing_product(self, service, db_session):
        """GIVEN a non-existent product WHEN restore_stock THEN no-op (no raise)."""
        # Should not raise — restore is best-effort
        await service._restore_stock(99999, 5)
