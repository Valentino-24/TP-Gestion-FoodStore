"""Fixtures for integration tests — seed data for CRUD tests."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def seed_categoria_integration(db_session: AsyncSession) -> int:
    """Create a sample category for integration tests. Returns its ID."""
    from app.models.categoria import Categoria
    cat = Categoria(nombre="Integración Test Cat", descripcion="For integration tests")
    db_session.add(cat)
    await db_session.flush()
    return cat.id


@pytest_asyncio.fixture
async def seed_producto_integration(
    db_session: AsyncSession,
    seed_categoria_integration: int,
) -> int:
    """Create a sample product for integration tests. Returns its ID."""
    from app.models.producto import Producto
    prod = Producto(
        nombre="Producto Integración",
        descripcion="Test",
        precio=25.50,
        categoria_id=seed_categoria_integration,
        activo=True,
    )
    db_session.add(prod)
    await db_session.flush()
    return prod.id
