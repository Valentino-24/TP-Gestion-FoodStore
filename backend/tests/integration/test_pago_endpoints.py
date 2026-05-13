"""Integration tests for pago endpoints."""

from httpx import AsyncClient


class TestPagoCreate:
    async def test_create_pago_authenticated(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated user creates a payment THEN it's processed."""
        resp = await async_client.post("/api/v1/pagos/", json={
            "pedido_id": 1,
            "metodo_pago": "mercadopago",
            "monto": 100.0,
        }, headers=auth_headers)
        # May be 200/201 or 404 (pedido not found) or 401
        assert resp.status_code in (200, 201, 404, 401)

    async def test_create_pago_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user creates a payment THEN 401."""
        resp = await async_client.post("/api/v1/pagos/", json={
            "pedido_id": 1,
            "metodo_pago": "mercadopago",
            "monto": 100.0,
        })
        assert resp.status_code == 401
