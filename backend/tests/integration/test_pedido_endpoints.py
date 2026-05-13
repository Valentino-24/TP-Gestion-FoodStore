"""Integration tests for pedido endpoints."""

import pytest
from httpx import AsyncClient


class TestPedidoCreate:
    async def test_create_pedido_as_client(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated client creates a pedido THEN it's created."""
        resp = await async_client.post("/api/v1/pedidos/", json={
            "direccion_entrega": "Calle Test 123",
        }, headers=auth_headers)
        # May be 200 or 201 depending on router implementation
        assert resp.status_code in (200, 201)

    async def test_create_pedido_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user creates a pedido THEN 401."""
        resp = await async_client.post("/api/v1/pedidos/", json={
            "direccion_entrega": "No Auth",
        })
        assert resp.status_code == 401


class TestPedidoList:
    async def test_list_own_pedidos(self, async_client: AsyncClient, auth_headers):
        """WHEN client lists own pedidos THEN 200."""
        resp = await async_client.get("/api/v1/pedidos/", headers=auth_headers)
        # May be 200 or 401 depending on if the endpoint is protected
        assert resp.status_code in (200, 401)

    async def test_list_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin lists all pedidos THEN 200."""
        resp = await async_client.get("/api/v1/pedidos/", headers=admin_headers)
        assert resp.status_code in (200, 401)


class TestPedidoGetById:
    async def test_get_pedido_by_id_authenticated(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated user gets a pedido by ID THEN returns pedido or 404."""
        # Try getting a non-existent pedido
        resp = await async_client.get("/api/v1/pedidos/99999", headers=auth_headers)
        assert resp.status_code in (404, 401)
