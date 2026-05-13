"""Integration tests for categoria CRUD endpoints."""

import pytest
from httpx import AsyncClient


class TestCategoriaCreate:
    async def test_create_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin creates a category THEN 201."""
        payload = {"nombre": "Nueva Categoría", "descripcion": "Test description"}
        resp = await async_client.post("/api/v1/categorias/", json=payload, headers=admin_headers)
        assert resp.status_code == 201  # Created
        data = resp.json()
        assert data["nombre"] == "Nueva Categoría"

    async def test_create_as_client_forbidden(self, async_client: AsyncClient, auth_headers):
        """WHEN non-admin creates a category THEN 403."""
        payload = {"nombre": "No Auth Cat"}
        resp = await async_client.post("/api/v1/categorias/", json=payload, headers=auth_headers)
        assert resp.status_code == 403

    async def test_create_duplicate_name(self, async_client: AsyncClient, admin_headers):
        """WHEN creating duplicate category name THEN 409."""
        payload = {"nombre": "Unique Cat"}
        resp1 = await async_client.post("/api/v1/categorias/", json=payload, headers=admin_headers)
        assert resp1.status_code == 201

        resp2 = await async_client.post("/api/v1/categorias/", json=payload, headers=admin_headers)
        assert resp2.status_code == 409


class TestCategoriaList:
    async def test_list_authenticated(self, async_client: AsyncClient, auth_headers, admin_headers):
        """WHEN authenticated user lists categories THEN 200."""
        # Create one first
        await async_client.post("/api/v1/categorias/", json={"nombre": "Listable"}, headers=admin_headers)

        resp = await async_client.get("/api/v1/categorias/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_list_unauthenticated(self, async_client: AsyncClient):
        """WHEN unauthenticated user lists categories THEN 401."""
        resp = await async_client.get("/api/v1/categorias/")
        assert resp.status_code == 401


class TestCategoriaGetById:
    async def test_get_by_id_found(self, async_client: AsyncClient, auth_headers, admin_headers):
        """WHEN getting existing category THEN 200."""
        create_resp = await async_client.post(
            "/api/v1/categorias/", json={"nombre": "Findable"}, headers=admin_headers,
        )
        cat_id = create_resp.json()["id"]

        resp = await async_client.get(f"/api/v1/categorias/{cat_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Findable"

    async def test_get_by_id_not_found(self, async_client: AsyncClient, auth_headers):
        """WHEN getting non-existent category THEN 404."""
        resp = await async_client.get("/api/v1/categorias/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestCategoriaUpdate:
    async def test_update_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin updates category THEN 200."""
        create_resp = await async_client.post(
            "/api/v1/categorias/", json={"nombre": "Updatable"}, headers=admin_headers,
        )
        cat_id = create_resp.json()["id"]

        resp = await async_client.put(
            f"/api/v1/categorias/{cat_id}",
            json={"nombre": "Updated"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Updated"

    async def test_update_as_client_forbidden(self, async_client: AsyncClient, auth_headers, admin_headers):
        """WHEN non-admin updates category THEN 403."""
        create_resp = await async_client.post(
            "/api/v1/categorias/", json={"nombre": "Forbidden Update"}, headers=admin_headers,
        )
        cat_id = create_resp.json()["id"]

        resp = await async_client.put(
            f"/api/v1/categorias/{cat_id}",
            json={"nombre": "Hacked"},
            headers=auth_headers,
        )
        assert resp.status_code == 403


class TestCategoriaDelete:
    async def test_delete_as_admin(self, async_client: AsyncClient, admin_headers):
        """WHEN admin deletes category THEN it's soft-deleted."""
        create_resp = await async_client.post(
            "/api/v1/categorias/", json={"nombre": "Deletable"}, headers=admin_headers,
        )
        cat_id = create_resp.json()["id"]

        resp = await async_client.delete(f"/api/v1/categorias/{cat_id}", headers=admin_headers)
        assert resp.status_code == 204

    async def test_delete_as_client_forbidden(self, async_client: AsyncClient, auth_headers, admin_headers):
        """WHEN non-admin deletes category THEN 403."""
        create_resp = await async_client.post(
            "/api/v1/categorias/", json={"nombre": "Protected"}, headers=admin_headers,
        )
        cat_id = create_resp.json()["id"]

        resp = await async_client.delete(f"/api/v1/categorias/{cat_id}", headers=auth_headers)
        assert resp.status_code == 403

    async def test_delete_not_found(self, async_client: AsyncClient, admin_headers):
        """WHEN deleting non-existent category THEN 404."""
        resp = await async_client.delete("/api/v1/categorias/99999", headers=admin_headers)
        assert resp.status_code == 404
