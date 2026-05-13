"""Shared fixtures for all backend tests."""

import asyncio
import os
import sys

# Windows requires SelectorEventLoopPolicy for asyncpg compatibility.
# MUST be set before any asyncpg imports.
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.config import settings
from app.database import get_db
from app.main import create_app

# ── Test database ────────────────────────────────────────────────

# Determine test database URL (default: foodstore_test on localhost:5432)
# Override via TEST_DATABASE_URL env var
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    settings.DATABASE_URL.rsplit("/", 1)[0] + "/foodstore_test",
)

# Use same connection params as dev but different database name
test_engine = create_async_engine(TEST_DB_URL, echo=False, pool_pre_ping=True)
test_async_session_maker = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def create_tables():
    """Create all tables before each test, drop after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    except Exception:
        pass  # Ignore cleanup errors (event loop may be closing)


# ── Database session fixture ─────────────────────────────────────

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the app's get_db dependency with test session."""
    async with test_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async with test_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── FastAPI app fixture ──────────────────────────────────────────

@pytest_asyncio.fixture
async def app() -> FastAPI:
    """Create the FastAPI app with test database override (no lifespan)."""
    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    # Disable lifespan to avoid production DB interference
    application.router.lifespan_context = None
    return application


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client with ASGI transport (no real server)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ── Seed data fixtures ───────────────────────────────────────────

@pytest_asyncio.fixture
async def seed_roles(db_session: AsyncSession):
    """Seed minimal role data needed for auth tests.

    Role IDs:
        1 = ADMIN, 2 = STOCK, 3 = PEDIDOS, 4 = CLIENT
    """
    from app.models.rol import Rol

    roles = [
        Rol(id=1, nombre="ADMIN", descripcion="Administrador"),
        Rol(id=2, nombre="STOCK", descripcion="Gestión de stock"),
        Rol(id=3, nombre="PEDIDOS", descripcion="Gestión de pedidos"),
        Rol(id=4, nombre="CLIENT", descripcion="Cliente"),
    ]
    for role in roles:
        db_session.add(role)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_categorias(db_session: AsyncSession):
    """Seed sample categories."""
    from app.models.categoria import Categoria

    categorias = [
        Categoria(id=1, nombre="Bebidas", descripcion="Bebidas y refrescos"),
        Categoria(id=2, nombre="Comidas", descripcion="Platos preparados"),
    ]
    for cat in categorias:
        db_session.add(cat)
    await db_session.flush()


# ── Auth fixtures ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client_token_data(async_client: AsyncClient, seed_roles) -> dict:
    """Register a CLIENT user and return token + user data."""
    register_payload = {
        "nombre": "Test",
        "apellido": "Client",
        "email": "client@test.com",
        "password": "password123",
    }
    resp = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "token_type": data["token_type"],
    }


@pytest_asyncio.fixture
async def auth_headers(client_token_data) -> dict[str, str]:
    """Bearer token headers for an authenticated CLIENT user."""
    token = client_token_data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_token_data(seed_roles, db_session: AsyncSession) -> dict:
    """Register an ADMIN user and return token + user data."""
    from app.models.usuario_rol import UsuarioRol
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash, create_access_token
    from app.config import settings
    from datetime import timedelta

    # Create admin user
    admin_user = Usuario(
        nombre="Admin",
        apellido="User",
        email="admin@test.com",
        password_hash=get_password_hash("admin1234"),
    )
    db_session.add(admin_user)
    await db_session.flush()

    # Assign ADMIN role (id=1)
    user_role = UsuarioRol(usuario_id=admin_user.id, rol_id=1)
    db_session.add(user_role)
    await db_session.commit()

    # Generate JWT directly (avoids circular app dependency)
    access_token = create_access_token(
        data={
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "roles": ["ADMIN"],
        },
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "refresh_token": "test-refresh-token",
        "token_type": "bearer",
    }


@pytest_asyncio.fixture
async def admin_headers(admin_token_data) -> dict[str, str]:
    """Bearer token headers for an authenticated ADMIN user."""
    token = admin_token_data["access_token"]
    return {"Authorization": f"Bearer {token}"}
