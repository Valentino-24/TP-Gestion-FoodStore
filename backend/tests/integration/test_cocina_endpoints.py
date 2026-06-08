"""Integration tests for Cocina (KDS) endpoints — SSE, REST, FSM role transitions."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def seed_cocina_rol(db_session: AsyncSession, seed_roles):
    """Add COCINA role (id=5) to the existing seed_roles."""
    from app.models.rol import Rol

    cocina = Rol(id=5, nombre="COCINA", descripcion="Cocina / KDS")
    db_session.add(cocina)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_estados(db_session: AsyncSession):
    """Seed estado_pedido entries needed for FK constraint."""
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
async def seed_formas_pago(db_session: AsyncSession):
    """Seed forma_pago entries."""
    from app.models.forma_pago import FormaPago

    formas = [
        FormaPago(id=1, nombre="Tarjeta de credito", activo=True),
        FormaPago(id=2, nombre="Efectivo", activo=True),
    ]
    for f in formas:
        db_session.add(f)
    await db_session.flush()


@pytest_asyncio.fixture
async def seed_categoria_cocina(db_session: AsyncSession) -> int:
    """Create a category and return its ID."""
    from app.models.categoria import Categoria

    cat = Categoria(nombre="Cocina Test", descripcion="Test cat")
    db_session.add(cat)
    await db_session.flush()
    return cat.id


@pytest_asyncio.fixture
async def seed_producto_cocina(db_session: AsyncSession, seed_categoria_cocina: int) -> int:
    """Create a product and return its ID."""
    from app.models.producto import Producto

    prod = Producto(
        nombre="Hamburguesa Test",
        descripcion="Test",
        precio=15.0,
        categoria_id=seed_categoria_cocina,
        activo=True,
        stock_cantidad=100,
    )
    db_session.add(prod)
    await db_session.flush()
    return prod.id


@pytest_asyncio.fixture
async def cocina_token_data(seed_cocina_rol, db_session: AsyncSession) -> dict:
    """Register a COCINA user and return token data."""
    from app.models.usuario_rol import UsuarioRol
    from app.models.usuario import Usuario
    from app.core.security import get_password_hash, create_access_token
    from app.config import settings
    from datetime import timedelta

    user = Usuario(
        nombre="Cocinero",
        apellido="Test",
        email="cocina@test.com",
        password_hash=get_password_hash("cocina123"),
    )
    db_session.add(user)
    await db_session.flush()

    user_role = UsuarioRol(usuario_id=user.id, rol_id=5)
    db_session.add(user_role)
    await db_session.commit()

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": ["COCINA"],
        },
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "refresh_token": "test-refresh",
        "token_type": "bearer",
    }


@pytest_asyncio.fixture
async def cocina_headers(cocina_token_data) -> dict[str, str]:
    """Bearer token headers for a COCINA user."""
    return {"Authorization": f"Bearer {cocina_token_data['access_token']}"}


@pytest_asyncio.fixture
async def seed_pedido_confirmado(
    db_session: AsyncSession,
    seed_estados,
    seed_formas_pago,
    seed_producto_cocina: int,
    admin_token_data,
) -> int:
    """Create a pedido in CONFIRMADO state for kitchen testing.

    Creates a pedido with one item, plus a historial entry so
    CocinaService can derive kitchen_entry_at. Returns the pedido ID.
    """
    from app.models.pedido import Pedido
    from app.models.pedido_item import PedidoItem
    from app.models.historial_estado import HistorialEstado
    from datetime import datetime, timezone

    pedido = Pedido(
        usuario_id=1,  # admin user (created by admin_token_data)
        estado="CONFIRMADO",
        total=15.0,
        forma_pago_id=1,
    )
    db_session.add(pedido)
    await db_session.flush()

    # Add an item
    item = PedidoItem(
        pedido_id=pedido.id,
        producto_id=seed_producto_cocina,
        producto_nombre="Hamburguesa Test",
        cantidad=1,
        precio_unitario=15.0,
        subtotal=15.0,
    )
    db_session.add(item)

    # Add historial entry for CONFIRMADO so kitchen_entry_at is derivable
    historial = HistorialEstado(
        pedido_id=pedido.id,
        estado_desde="PENDIENTE",
        estado_hasta="CONFIRMADO",
        usuario_id=1,
    )
    db_session.add(historial)
    await db_session.commit()

    return pedido.id


@pytest_asyncio.fixture
async def seed_pedido_en_preparacion(
    db_session: AsyncSession,
    seed_pedido_confirmado: int,
) -> int:
    """Create a pedido in EN_PREPARACION state.

    Uses an existing pedido and sets its estado directly for test simplicity.
    """
    from app.models.pedido import Pedido

    result = await db_session.execute(
        select(Pedido).where(Pedido.id == seed_pedido_confirmado)
    )
    pedido = result.scalar_one()
    pedido.estado = "EN_PREPARACION"
    await db_session.commit()

    return pedido.id


# ── Task 10.2: GET /cocina/pedidos ──────────────────────────────────────────


class TestListPedidosCocina:
    """GET /api/v1/cocina/pedidos — list pedidos in kitchen states."""

    @pytest.mark.asyncio
    async def test_cocina_user_gets_pedidos_confirmado(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """COCINA user sees pedidos in CONFIRMADO state."""
        resp = await async_client.get("/api/v1/cocina/pedidos", headers=cocina_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        ids = [p["id"] for p in data]
        assert seed_pedido_confirmado in ids, f"Pedido {seed_pedido_confirmado} not in response"

    @pytest.mark.asyncio
    async def test_admin_gets_pedidos(
        self, async_client: AsyncClient, admin_headers, seed_pedido_confirmado: int,
    ):
        """ADMIN user can also list kitchen pedidos."""
        resp = await async_client.get("/api/v1/cocina/pedidos", headers=admin_headers)
        assert resp.status_code == 200
        ids = [p["id"] for p in resp.json()]
        assert seed_pedido_confirmado in ids

    @pytest.mark.asyncio
    async def test_client_user_gets_403(
        self, async_client: AsyncClient, auth_headers,
    ):
        """CLIENT user gets 403 Forbidden on cocina endpoint."""
        resp = await async_client.get("/api/v1/cocina/pedidos", headers=auth_headers)
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"

    @pytest.mark.asyncio
    async def test_unauthenticated_gets_401(
        self, async_client: AsyncClient,
    ):
        """Unauthenticated user gets 401."""
        resp = await async_client.get("/api/v1/cocina/pedidos")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_response_fields(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """Response contains required KDS fields."""
        resp = await async_client.get("/api/v1/cocina/pedidos", headers=cocina_headers)
        assert resp.status_code == 200
        if resp.json():
            p = resp.json()[0]
            assert "id" in p
            assert "estado" in p
            assert "kitchen_entry_at" in p
            assert "items" in p
            assert "creado_en" in p


# ── Task 10.3: GET /cocina/eventos (SSE) ───────────────────────────────────


class TestSSEEventStream:
    """GET /api/v1/cocina/eventos — SSE event stream."""

    @pytest.mark.asyncio
    async def test_sse_returns_event_stream(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """COCINA user can connect to SSE endpoint and receives 'connected' event."""
        async with async_client.stream(
            "GET", "/api/v1/cocina/eventos", headers=cocina_headers, timeout=3.0,
        ) as response:
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            assert response.headers.get("content-type", "").startswith("text/event-stream"), \
                f"Expected text/event-stream, got {response.headers.get('content-type')}"

            # Read first chunk (should contain "event: connected") then close
            body = ""
            try:
                async for line in response.aiter_lines():
                    body += line + "\n"
                    if "event: connected" in body:
                        break
            except Exception:
                pass

            assert "event: connected" in body, f"Expected 'event: connected', got:\n{body}"

    @pytest.mark.asyncio
    async def test_sse_client_user_gets_403(
        self, async_client: AsyncClient, auth_headers,
    ):
        """CLIENT user gets 403 on SSE endpoint."""
        resp = await async_client.get("/api/v1/cocina/eventos", headers=auth_headers)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_sse_unauthenticated_gets_401(
        self, async_client: AsyncClient,
    ):
        """Unauthenticated user gets 401 on SSE endpoint."""
        resp = await async_client.get("/api/v1/cocina/eventos")
        assert resp.status_code == 401


# ── Task 10.4: PATCH /pedidos/{id}/estado - transition validation per role ──


class TestPedidoEstadoTransitions:
    """PATCH /api/v1/pedidos/{id}/estado — role-based FSM transition validation."""

    @pytest.mark.asyncio
    async def test_cocina_confirmado_to_en_preparacion(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """COCINA can transition CONFIRMADO → EN_PREPARACION."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "EN_PREPARACION"},
            headers=cocina_headers,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json()["estado"] == "EN_PREPARACION"

    @pytest.mark.asyncio
    async def test_cocina_en_preparacion_to_en_camino(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_en_preparacion: int,
    ):
        """COCINA can transition EN_PREPARACION → EN_CAMINO."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_en_preparacion}/estado",
            json={"estado": "EN_CAMINO"},
            headers=cocina_headers,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        assert resp.json()["estado"] == "EN_CAMINO"

    @pytest.mark.asyncio
    async def test_cocina_cannot_skip_to_entregado(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """COCINA cannot transition CONFIRMADO → ENTREGADO (must go through EN_PREPARACION + EN_CAMINO)."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "ENTREGADO"},
            headers=cocina_headers,
        )
        # Should fail FSM validation first — CONFIRMED→ENTREGADO is not a valid FSM transition
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    @pytest.mark.asyncio
    async def test_cocina_cannot_set_same_estado(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """Setting estado to same value fails FSM validation (400)."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "CONFIRMADO"},
            headers=cocina_headers,
        )
        # CONFIRMADO → CONFIRMADO is not in ESTADO_TRANSITIONS
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"

    @pytest.mark.asyncio
    async def test_admin_can_do_any_transition(
        self, async_client: AsyncClient, admin_headers, seed_pedido_confirmado: int,
    ):
        """ADMIN can transition CONFIRMADO → EN_PREPARACION."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "EN_PREPARACION"},
            headers=admin_headers,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    @pytest.mark.asyncio
    async def test_client_gets_403_on_estado_update(
        self, async_client: AsyncClient, auth_headers, seed_pedido_confirmado: int,
    ):
        """CLIENT user gets 403 on estado update (not in allowed roles)."""
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "EN_PREPARACION"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_invalid_fsm_transition_returns_400(
        self, async_client: AsyncClient, cocina_headers, seed_pedido_confirmado: int,
    ):
        """EN_PREPARACION → PENDIENTE is not a valid FSM transition (400)."""
        # First transition to EN_PREPARACION
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "EN_PREPARACION"},
            headers=cocina_headers,
        )
        assert resp.status_code == 200

        # Then try to go back to PENDIENTE (not allowed by FSM)
        resp = await async_client.patch(
            f"/api/v1/pedidos/{seed_pedido_confirmado}/estado",
            json={"estado": "PENDIENTE"},
            headers=cocina_headers,
        )
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
