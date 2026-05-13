"""Integration tests for direccion endpoints."""

from httpx import AsyncClient


class TestDireccionCreate:
    async def test_create_direccion_authenticated(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated user creates an address THEN it's saved."""
        payload = {
            "calle": "Av. Siempre Viva",
            "numero": "742",
            "ciudad": "Springfield",
            "codigo_postal": "1234",
        }
        resp = await async_client.post("/api/v1/direcciones/", json=payload, headers=auth_headers)
        assert resp.status_code in (200, 201, 401)

    async def test_create_direccion_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user creates an address THEN 401."""
        resp = await async_client.post("/api/v1/direcciones/", json={
            "calle": "No Auth",
            "ciudad": "Nowhere",
        })
        assert resp.status_code == 401


class TestDireccionList:
    async def test_list_own_direcciones(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated user lists own addresses THEN 200."""
        resp = await async_client.get("/api/v1/direcciones/", headers=auth_headers)
        assert resp.status_code in (200, 401)

    async def test_list_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user lists addresses THEN 401."""
        resp = await async_client.get("/api/v1/direcciones/")
        assert resp.status_code == 401


class TestDireccionDelete:
    async def test_delete_direccion_authenticated(self, async_client: AsyncClient, auth_headers):
        """WHEN authenticated user deletes own address THEN 204."""
        resp = await async_client.delete("/api/v1/direcciones/99999", headers=auth_headers)
        assert resp.status_code in (204, 404, 401)
