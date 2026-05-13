"""Fixtures for unit tests — module-specific test data."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def sample_category(db_session: AsyncSession) -> int:
    """Create a sample category and return its ID."""
    from app.models.categoria import Categoria

    cat = Categoria(nombre="Test Category", descripcion="A test category")
    db_session.add(cat)
    await db_session.flush()
    return cat.id


@pytest_asyncio.fixture
async def sample_product(db_session: AsyncSession, sample_category: int) -> int:
    """Create a sample product and return its ID."""
    from app.models.producto import Producto

    prod = Producto(
        nombre="Test Product",
        descripcion="A test product",
        precio=10.50,
        categoria_id=sample_category,
        activo=True,
    )
    db_session.add(prod)
    await db_session.flush()
    return prod.id


@pytest_asyncio.fixture
async def sample_cliente(db_session: AsyncSession) -> int:
    """Create a sample customer and return its ID."""
    from app.models.cliente import Cliente

    cli = Cliente(
        nombre="Juan",
        apellido="Perez",
        email="juan@test.com",
        telefono="123456789",
        direccion="Calle Falsa 123",
        activo=True,
    )
    db_session.add(cli)
    await db_session.flush()
    return cli.id
