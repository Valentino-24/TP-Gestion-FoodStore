"""Integration tests for producto CRUD endpoints."""

from httpx import AsyncClient


class TestProductoCreate:
    async def test_create_as_admin(self, async_client: AsyncClient, admin_headers, seed_categoria_integration):
        """WHEN admin creates a product THEN 200."""
        payload = {
            "nombre": "Nuevo Producto",
            "precio": 15.99,
            "categoria_id": seed_categoria_integration,
        }
        resp = await async_client.post("/api/v1/productos/", json=payload, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Nuevo Producto"
        assert data["precio"] == 15.99
        assert data["activo"] is True

    async def test_create_as_client_forbidden(self, async_client: AsyncClient, auth_headers, seed_categoria_integration):
        """WHEN non-admin creates product THEN 403."""
        payload = {
            "nombre": "No Auth",
            "precio": 10.0,
            "categoria_id": seed_categoria_integration,
        }
        resp = await async_client.post("/api/v1/productos/", json=payload, headers=auth_headers)
        assert resp.status_code == 403

    async def test_create_invalid_categoria(self, async_client: AsyncClient, admin_headers):
        """WHEN creating with non-existent categoria_id THEN 404."""
        payload = {
            "nombre": "Bad Cat",
            "precio": 10.0,
            "categoria_id": 99999,
        }
        resp = await async_client.post("/api/v1/productos/", json=payload, headers=admin_headers)
        assert resp.status_code == 404

    async def test_create_negative_price(self, async_client: AsyncClient, admin_headers, seed_categoria_integration):
        """WHEN creating with negative price THEN 422."""
        payload = {
            "nombre": "Negative",
            "precio": -5.0,
            "categoria_id": seed_categoria_integration,
        }
        resp = await async_client.post("/api/v1/productos/", json=payload, headers=admin_headers)
        assert resp.status_code == 422


class TestProductoList:
    async def test_list_authenticated(self, async_client: AsyncClient, auth_headers, admin_headers, seed_categoria_integration):
        """WHEN authenticated user lists products THEN 200 with paginated response."""
        # Create a product first
        await async_client.post("/api/v1/productos/", json={
            "nombre": "Listable Prod", "precio": 10.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)

        resp = await async_client.get("/api/v1/productos/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    async def test_list_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user lists products THEN 401."""
        resp = await async_client.get("/api/v1/productos/")
        assert resp.status_code == 401

    async def test_list_filter_by_categoria(self, async_client: AsyncClient, auth_headers, admin_headers):
        """WHEN filtering by categoria_id THEN only matching products."""
        # Create two categories and one product each
        cat1_resp = await async_client.post("/api/v1/categorias/", json={"nombre": "Cat Filter 1"}, headers=admin_headers)
        cat1_id = cat1_resp.json()["id"]
        cat2_resp = await async_client.post("/api/v1/categorias/", json={"nombre": "Cat Filter 2"}, headers=admin_headers)
        cat2_id = cat2_resp.json()["id"]

        await async_client.post("/api/v1/productos/", json={
            "nombre": "In Cat1", "precio": 5.0, "categoria_id": cat1_id,
        }, headers=admin_headers)
        await async_client.post("/api/v1/productos/", json={
            "nombre": "In Cat2", "precio": 5.0, "categoria_id": cat2_id,
        }, headers=admin_headers)

        resp = await async_client.get(f"/api/v1/productos/?categoria_id={cat1_id}", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["nombre"] == "In Cat1"


class TestProductoGetById:
    async def test_get_by_id_found(self, async_client: AsyncClient, auth_headers, admin_headers, seed_categoria_integration):
        """WHEN getting existing product THEN 200."""
        create_resp = await async_client.post("/api/v1/productos/", json={
            "nombre": "Findable Prod", "precio": 20.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)
        prod_id = create_resp.json()["id"]

        resp = await async_client.get(f"/api/v1/productos/{prod_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Findable Prod"

    async def test_get_by_id_not_found(self, async_client: AsyncClient, auth_headers):
        """WHEN getting non-existent product THEN 404."""
        resp = await async_client.get("/api/v1/productos/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestProductoUpdate:
    async def test_update_as_admin(self, async_client: AsyncClient, admin_headers, seed_categoria_integration):
        """WHEN admin updates product THEN 200."""
        create_resp = await async_client.post("/api/v1/productos/", json={
            "nombre": "Updatable Prod", "precio": 10.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)
        assert create_resp.status_code == 201
        prod_id = create_resp.json()["id"]

        resp = await async_client.put(f"/api/v1/productos/{prod_id}", json={
            "nombre": "Updated Prod", "precio": 15.0,
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Updated Prod"
        assert resp.json()["precio"] == 15.0

    async def test_update_as_client_forbidden(self, async_client: AsyncClient, auth_headers, admin_headers, seed_categoria_integration):
        """WHEN non-admin updates product THEN 403."""
        create_resp = await async_client.post("/api/v1/productos/", json={
            "nombre": "Protected Prod", "precio": 10.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)
        prod_id = create_resp.json()["id"]

        resp = await async_client.put(f"/api/v1/productos/{prod_id}", json={
            "nombre": "Hacked",
        }, headers=auth_headers)
        assert resp.status_code == 403


class TestProductoDelete:
    async def test_delete_as_admin(self, async_client: AsyncClient, admin_headers, seed_categoria_integration):
        """WHEN admin deletes product THEN 204 (soft-delete)."""
        create_resp = await async_client.post("/api/v1/productos/", json={
            "nombre": "Deletable Prod", "precio": 10.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)
        assert create_resp.status_code == 201
        prod_id = create_resp.json()["id"]

        resp = await async_client.delete(f"/api/v1/productos/{prod_id}", headers=admin_headers)
        assert resp.status_code == 204

    async def test_delete_as_client_forbidden(self, async_client: AsyncClient, auth_headers, admin_headers, seed_categoria_integration):
        """WHEN non-admin deletes product THEN 403."""
        create_resp = await async_client.post("/api/v1/productos/", json={
            "nombre": "Protected Del", "precio": 10.0, "categoria_id": seed_categoria_integration,
        }, headers=admin_headers)
        prod_id = create_resp.json()["id"]

        resp = await async_client.delete(f"/api/v1/productos/{prod_id}", headers=auth_headers)
        assert resp.status_code == 403
