"""Integration tests for auth endpoints (register, login, refresh, logout, me)."""

import pytest
from httpx import AsyncClient


class TestAuthRegister:
    async def test_register_success(self, async_client: AsyncClient):
        """WHEN registering with valid data THEN 201 + tokens."""
        payload = {
            "nombre": "New",
            "apellido": "User",
            "email": "newuser@test.com",
            "password": "securepass123",
        }
        resp = await async_client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_register_duplicate_email(self, async_client: AsyncClient, seed_roles):
        """WHEN registering with existing email THEN 409."""
        # First registration
        payload = {
            "nombre": "First",
            "apellido": "User",
            "email": "dup@test.com",
            "password": "securepass123",
        }
        resp1 = await async_client.post("/api/v1/auth/register", json=payload)
        assert resp1.status_code == 201

        # Second registration with same email
        resp2 = await async_client.post("/api/v1/auth/register", json=payload)
        assert resp2.status_code == 409
        assert "ya esta registrado" in resp2.text

    async def test_register_weak_password(self, async_client: AsyncClient):
        """WHEN registering with short password THEN 422."""
        payload = {
            "nombre": "Weak",
            "apellido": "Pass",
            "email": "weak@test.com",
            "password": "short",
        }
        resp = await async_client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422


class TestAuthLogin:
    async def test_login_success(self, async_client: AsyncClient, seed_roles):
        """WHEN logging in with valid credentials THEN 200 + tokens."""
        # Register first
        await async_client.post("/api/v1/auth/register", json={
            "nombre": "Login",
            "apellido": "Test",
            "email": "login@test.com",
            "password": "securepass123",
        })

        # Login
        payload = {"email": "login@test.com", "password": "securepass123"}
        resp = await async_client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """WHEN logging in with wrong password THEN 401."""
        payload = {"email": "noone@test.com", "password": "wrongpassword"}
        resp = await async_client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code == 401
        assert "Credenciales invalidas" in resp.text

    async def test_login_wrong_password_returns_same_error(self, async_client: AsyncClient, seed_roles):
        """WHEN wrong password THEN same error as non-existent user."""
        await async_client.post("/api/v1/auth/register", json={
            "nombre": "Sec", "apellido": "Test",
            "email": "sec@test.com", "password": "securepass123",
        })

        payload = {"email": "sec@test.com", "password": "wrongpass"}
        resp = await async_client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales invalidas"


class TestAuthMe:
    async def test_get_me_authenticated(self, async_client: AsyncClient, auth_headers):
        """WHEN GET /me with valid token THEN 200 + user data."""
        resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "email" in data
        assert "roles" in data

    async def test_get_me_returns_roles(self, async_client: AsyncClient, auth_headers):
        """WHEN GET /me THEN response includes roles array."""
        resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        data = resp.json()
        assert "CLIENT" in data["roles"]

    async def test_get_me_unauthenticated(self, async_client: AsyncClient):
        """WHEN GET /me without token THEN 401."""
        resp = await async_client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_get_me_with_bad_token(self, async_client: AsyncClient):
        """WHEN GET /me with invalid token THEN 401."""
        headers = {"Authorization": "Bearer invalidtoken123"}
        resp = await async_client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 401


class TestAuthRefresh:
    async def test_refresh_success(self, async_client: AsyncClient, seed_roles):
        """WHEN refreshing with valid token THEN 200 + new tokens."""
        # Register
        reg_resp = await async_client.post("/api/v1/auth/register", json={
            "nombre": "Refresh", "apellido": "Test",
            "email": "refresh@test.com", "password": "securepass123",
        })
        refresh_token = reg_resp.json()["refresh_token"]

        # Refresh
        resp = await async_client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # Token rotation: new refresh token should be different
        assert data["refresh_token"] != refresh_token

    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """WHEN refreshing with invalid token THEN 401."""
        resp = await async_client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid-refresh-token",
        })
        assert resp.status_code == 401


class TestAuthLogout:
    async def test_logout_success(self, async_client: AsyncClient, seed_roles):
        """WHEN logging out with valid token THEN 204."""
        # Register
        reg_resp = await async_client.post("/api/v1/auth/register", json={
            "nombre": "Logout", "apellido": "Test",
            "email": "logout@test.com", "password": "securepass123",
        })
        refresh_token = reg_resp.json()["refresh_token"]

        # Logout
        resp = await async_client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 204

    async def test_logout_idempotent(self, async_client: AsyncClient, seed_roles):
        """WHEN logging out twice THEN both return 204."""
        reg_resp = await async_client.post("/api/v1/auth/register", json={
            "nombre": "Idem", "apellido": "Test",
            "email": "idem@test.com", "password": "securepass123",
        })
        refresh_token = reg_resp.json()["refresh_token"]

        # First logout
        resp1 = await async_client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert resp1.status_code == 204

        # Second logout with same token (idempotent)
        resp2 = await async_client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert resp2.status_code == 204
