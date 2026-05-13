"""Integration tests for cliente CRUD endpoints."""

from httpx import AsyncClient


class TestClienteCreate:
    async def test_create_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin creates a customer THEN 200."""
        payload = {
            "nombre": "Carlos",
            "apellido": "Garcia",
            "email": "carlos@test.com",
            "telefono": "123456789",
        }
        resp = await async_client.post("/api/v1/clientes/", json=payload, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Carlos"
        assert data["email"] == "carlos@test.com"

    async def test_create_duplicate_email(self, async_client: AsyncClient, admin_headers):
        """WHEN creating customer with existing email THEN 422."""
        payload = {
            "nombre": "First",
            "apellido": "User",
            "email": "dupe@test.com",
        }
        resp1 = await async_client.post("/api/v1/clientes/", json=payload, headers=admin_headers)
        assert resp1.status_code == 201

        resp2 = await async_client.post("/api/v1/clientes/", json=payload, headers=admin_headers)
        assert resp2.status_code == 422


class TestClienteList:
    async def test_list_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin lists customers THEN 200."""
        # Create one
        await async_client.post("/api/v1/clientes/", json={
            "nombre": "Listable", "apellido": "Client", "email": "list@test.com",
        }, headers=admin_headers)

        resp = await async_client.get("/api/v1/clientes/", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_list_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user lists customers THEN 401."""
        resp = await async_client.get("/api/v1/clientes/")
        assert resp.status_code == 401


class TestClienteGetById:
    async def test_get_by_id_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin gets customer by ID THEN 200."""
        create_resp = await async_client.post("/api/v1/clientes/", json={
            "nombre": "Findable", "apellido": "Client", "email": "find@test.com",
        }, headers=admin_headers)
        cli_id = create_resp.json()["id"]

        resp = await async_client.get(f"/api/v1/clientes/{cli_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == cli_id

    async def test_get_by_id_not_found(self, async_client: AsyncClient, admin_headers):
        """WHEN getting non-existent customer THEN 404."""
        resp = await async_client.get("/api/v1/clientes/99999", headers=admin_headers)
        assert resp.status_code == 404


class TestClienteUpdate:
    async def test_update_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin updates customer THEN 200."""
        create_resp = await async_client.post("/api/v1/clientes/", json={
            "nombre": "Old Name", "apellido": "Client", "email": "oldname@test.com",
        }, headers=admin_headers)
        cli_id = create_resp.json()["id"]

        resp = await async_client.put(f"/api/v1/clientes/{cli_id}", json={
            "nombre": "New Name",
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "New Name"

    async def test_update_not_found(self, async_client: AsyncClient, admin_headers):
        """WHEN updating non-existent customer THEN 404."""
        resp = await async_client.put("/api/v1/clientes/99999", json={
            "nombre": "Ghost",
        }, headers=admin_headers)
        assert resp.status_code == 404


class TestClienteDelete:
    async def test_delete_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin deletes customer THEN 204 (soft-delete)."""
        create_resp = await async_client.post("/api/v1/clientes/", json={
            "nombre": "Deletable", "apellido": "Client", "email": "del@test.com",
        }, headers=admin_headers)
        cli_id = create_resp.json()["id"]

        resp = await async_client.delete(f"/api/v1/clientes/{cli_id}", headers=admin_headers)
        assert resp.status_code == 204

    async def test_delete_not_found(self, async_client: AsyncClient, admin_headers):
        """WHEN deleting non-existent customer THEN 404."""
        resp = await async_client.delete("/api/v1/clientes/99999", headers=admin_headers)
        assert resp.status_code == 404
