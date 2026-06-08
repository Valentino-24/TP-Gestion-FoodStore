"""Integration tests for historial_estado — verifying historial is created through API flow."""

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def seed_estados(db_session: AsyncSession) -> None:
    """Seed estado_pedido entries needed for FK constraint on Pedido.estado."""
    from app.models.estado_pedido import EstadoPedido
    estados = [
        EstadoPedido(id=1, nombre="PENDIENTE", descripcion="Esperando confirmacion"),
        EstadoPedido(id=2, nombre="CONFIRMADO", descripcion="Pago confirmado"),
        EstadoPedido(id=3, nombre="EN_PREPARACION", descripcion="Preparando"),
        EstadoPedido(id=4, nombre="EN_CAMINO", descripcion="Enviado"),
        EstadoPedido(id=5, nombre="ENTREGADO", descripcion="Entregado"),
        EstadoPedido(id=6, nombre="CANCELADO", descripcion="Cancelado"),
    ]
    for e in estados:
        db_session.add(e)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_formas_pago(db_session: AsyncSession) -> None:
    """Seed forma_pago entries."""
    from app.models.forma_pago import FormaPago
    formas = [
        FormaPago(id=1, nombre="Tarjeta de credito", activo=True),
        FormaPago(id=2, nombre="Tarjeta de debito", activo=True),
        FormaPago(id=3, nombre="Efectivo", activo=True),
    ]
    for f in formas:
        db_session.add(f)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_pedido_data(
    db_session: AsyncSession,
    seed_estados,
    seed_formas_pago,
) -> dict:
    """Seed complete data for a pedido test and return IDs."""
    from app.models.categoria import Categoria
    from app.models.producto import Producto
    from app.models.direccion import Direccion

    # Category
    cat = Categoria(nombre="Test Integración", descripcion="Test cat")
    db_session.add(cat)
    await db_session.flush()

    # Product with stock
    prod = Producto(
        nombre="Producto Stock",
        descripcion="Test",
        precio=100.0,
        categoria_id=cat.id,
        activo=True,
        stock_cantidad=20,
    )
    db_session.add(prod)
    await db_session.flush()

    # Create a user directly (not via endpoint) and get id
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash
    user = Usuario(
        nombre="Pedido",
        apellido="Tester",
        email="pedido_tester@test.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(user)
    await db_session.flush()

    # Address for the user
    direccion = Direccion(
        usuario_id=user.id,
        calle="Av. Siempre Viva",
        numero="742",
        ciudad="Springfield",
        provincia="BSAS",
        codigo_postal="1000",
        telefono_contacto="123456789",
    )
    db_session.add(direccion)
    await db_session.commit()

    return {
        "user_id": user.id,
        "producto_id": prod.id,
        "direccion_id": direccion.id,
        "categoria_id": cat.id,
    }


@pytest_asyncio.fixture
async def client_auth_headers(async_client: AsyncClient) -> dict[str, str]:
    """Register a client and return auth headers."""
    resp = await async_client.post("/api/v1/auth/register", json={
        "nombre": "Historial",
        "apellido": "Test",
        "email": "historial_test@test.com",
        "password": "password123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestHistorialOnCreate:
    async def test_creates_historial_on_pedido_creation(
        self, async_client: AsyncClient, client_auth_headers, seed_pedido_data
    ):
        """GIVEN an authenticated client WHEN creating a pedido THEN historial includes PENDIENTE entry."""
        data = seed_pedido_data
        resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Producto Stock",
                "cantidad": 2,
                "precio_unitario": 100.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=client_auth_headers)

        assert resp.status_code == 201, f"Create pedido failed: {resp.text}"
        pedido = resp.json()

        assert "historial" in pedido
        assert len(pedido["historial"]) >= 1

        initial = pedido["historial"][0]
        assert initial["estado_hasta"] == "PENDIENTE"
        assert initial["estado_desde"] is None
        assert initial["observacion"] == "Pedido creado"


class TestHistorialOnTransition:
    async def test_creates_historial_on_state_transition(
        self, async_client: AsyncClient, client_auth_headers, seed_pedido_data, admin_headers
    ):
        """GIVEN an existing pedido WHEN admin transitions to CONFIRMADO THEN historial is recorded."""
        data = seed_pedido_data

        # Create pedido as client
        create_resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Producto Stock",
                "cantidad": 1,
                "precio_unitario": 100.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=client_auth_headers)
        assert create_resp.status_code == 201
        pedido_id = create_resp.json()["id"]

        # Transition to CONFIRMADO as admin
        transition_resp = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert transition_resp.status_code == 200, f"Transition failed: {transition_resp.text}"
        pedido = transition_resp.json()

        # Verify historial has both entries
        assert len(pedido["historial"]) >= 2

        # The second entry should be the transition
        transition_entry = pedido["historial"][1]
        assert transition_entry["estado_desde"] == "PENDIENTE"
        assert transition_entry["estado_hasta"] == "CONFIRMADO"
        assert "Transición" in (transition_entry.get("observacion") or "")

    async def test_historial_includes_all_transitions(
        self, async_client: AsyncClient, client_auth_headers, seed_pedido_data, admin_headers
    ):
        """GIVEN multiple state transitions WHEN GET pedido THEN historial shows all."""
        data = seed_pedido_data

        # Create pedido
        create_resp = await async_client.post("/api/v1/pedidos/", json={
            "items": [{
                "producto_id": data["producto_id"],
                "producto_nombre": "Producto Stock",
                "cantidad": 1,
                "precio_unitario": 100.0,
            }],
            "direccion_id": data["direccion_id"],
            "forma_pago_id": 1,
        }, headers=client_auth_headers)
        assert create_resp.status_code == 201
        pedido_id = create_resp.json()["id"]

        # Admin: PENDIENTE → CONFIRMADO
        r1 = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert r1.status_code == 200

        # Admin: CONFIRMADO → CANCELADO
        r2 = await async_client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"estado": "CANCELADO"},
            headers=admin_headers,
        )
        assert r2.status_code == 200
        pedido = r2.json()

        assert len(pedido["historial"]) >= 3

        estados = [h["estado_hasta"] for h in pedido["historial"]]
        assert "PENDIENTE" in estados
        assert "CONFIRMADO" in estados
        assert "CANCELADO" in estados

        # Verify chronological order
        from datetime import datetime
        timestamps = [datetime.fromisoformat(h["creado_en"]) for h in pedido["historial"]]
        assert timestamps == sorted(timestamps), "Historial entries must be in chronological order"
