"""Integration tests for stock management — verifying stock changes through API flow."""

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def seed_estados(db_session: AsyncSession) -> None:
    from app.models.estado_pedido import EstadoPedido
    estados = [
        EstadoPedido(id=1, nombre="PENDIENTE", descripcion="Esperando confirmacion"),
        EstadoPedido(id=2, nombre="CONFIRMADO", descripcion="Pago confirmado"),
        EstadoPedido(id=6, nombre="CANCELADO", descripcion="Cancelado"),
    ]
    for e in estados:
        db_session.add(e)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_formas_pago(db_session: AsyncSession) -> None:
    from app.models.forma_pago import FormaPago
    formas = [
        FormaPago(id=1, nombre="Tarjeta de credito", activo=True),
    ]
    for f in formas:
        db_session.add(f)
    await db_session.flush()


@pytest_asyncio.fixture
async def stock_test_data(
    db_session: AsyncSession,
    seed_estados,
    seed_formas_pago,
) -> dict:
    """Seed data for stock tests and return IDs."""
    from app.models.categoria import Categoria
    from app.models.producto import Producto
    from app.models.direccion import Direccion
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash

    cat = Categoria(nombre="Stock Test Cat", descripcion="Test")
    db_session.add(cat)
    await db_session.flush()

    # Product with stock=10
    prod = Producto(
        nombre="Stock Product",
        descripcion="Test stock",
        precio=50.0,
        categoria_id=cat.id,
        activo=True,
        stock_cantidad=10,
    )
    db_session.add(prod)
    await db_session.flush()

    # Client user
    user = Usuario(
        nombre="Stock",
        apellido="Tester",
        email="stock_tester@test.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(user)
    await db_session.flush()

    # Address
    direccion = Direccion(
        usuario_id=user.id,
        calle="Calle Stock",
        numero="100",
        ciudad="Test City",
        provincia="Test",
        codigo_postal="1234",
        telefono_contacto="111111111",
    )
    db_session.add(direccion)
    await db_session.commit()

    return {
        "user_id": user.id,
        "producto_id": prod.id,
        "direccion_id": direccion.id,
    }


@pytest_asyncio.fixture
async def stock_auth_headers(async_client: AsyncClient) -> dict[str, str]:
    """Register a stock test client and return auth headers."""
    resp = await async_client.post("/api/v1/auth/register", json={
        "nombre": "StockClient",
        "apellido": "Test",
        "email": "stock_client@test.com",
        "password": "password123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _get_stock(db_session, producto_id):
    """Helper to get current stock for a product."""
    from app.models.producto import Producto
    from sqlalchemy import select
    result = await db_session.execute(select(Producto).where(Producto.id == producto_id))
    return result.scalar_one().stock_cantidad


class TestStockDecrementOnConfirm:
    async def test_stock_decreases_when_pedido_confirmed(
        self, async_client: AsyncClient, stock_auth_headers, stock_test_data, admin_headers
    ):
        """GIVEN a pedido with a product WHEN confirmed THEN stock decreases."""
        data = stock_test_data

        # Create pedido
        create_resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Stock Product",
                "cantidad": 3,
                "precio_unitario": 50.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=stock_auth_headers)
        assert create_resp.status_code == 201
        pedido_id = create_resp.json()["id"]

        # Transition CONFIRMADO (triggers decrement)
        confirm_resp = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert confirm_resp.status_code == 200

        # Stock should be 10 - 3 = 7
        from app.database import get_db
        async for session in get_db():
            stock = await _get_stock(session, data["producto_id"])
            assert stock == 7, f"Expected stock=7, got {stock}"

    async def test_stock_restored_on_cancel(
        self, async_client: AsyncClient, stock_auth_headers, stock_test_data, admin_headers
    ):
        """GIVEN a confirmed pedido WHEN cancelled THEN stock is restored."""
        data = stock_test_data

        # Create pedido
        create_resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Stock Product",
                "cantidad": 2,
                "precio_unitario": 50.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=stock_auth_headers)
        assert create_resp.status_code == 201
        pedido_id = create_resp.json()["id"]

        # Confirm
        r1 = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert r1.status_code == 200

        # Cancel
        r2 = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CANCELADO"},
            headers=admin_headers,
        )
        assert r2.status_code == 200

        # Stock should be back to 10
        from app.database import get_db
        async for session in get_db():
            stock = await _get_stock(session, data["producto_id"])
            assert stock == 10, f"Expected stock=10, got {stock}"


class TestStockInsufficientError:
    async def test_returns_400_when_insufficient_stock(
        self, async_client: AsyncClient, stock_auth_headers, stock_test_data, admin_headers
    ):
        """GIVEN a pedido with items exceeding stock WHEN confirm THEN 400 error."""
        data = stock_test_data

        # Create pedido asking for 20 units (stock is only 10)
        create_resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Stock Product",
                "cantidad": 20,
                "precio_unitario": 50.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=stock_auth_headers)
        assert create_resp.status_code == 201
        pedido_id = create_resp.json()["id"]

        # Try to confirm — should fail with 400
        confirm_resp = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert confirm_resp.status_code == 400
        assert "Stock insuficiente" in confirm_resp.text
