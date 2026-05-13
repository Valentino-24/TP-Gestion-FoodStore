"""Tests for ClienteService business logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.clientes.service import ClienteService
from app.clientes.schemas import ClienteCreate, ClienteUpdate
from app.models.cliente import Cliente


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_active = AsyncMock()
    repo.count_active = AsyncMock()
    return repo


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_repo, mock_db):
    return ClienteService(repo=mock_repo, db=mock_db)


class TestClienteServiceCreate:
    async def test_create_success(self, service, mock_repo):
        """WHEN creating with valid data THEN cliente is created."""
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = Cliente(
            id=1, nombre="Juan", apellido="Perez",
            email="juan@test.com", telefono="123", activo=True,
        )

        data = ClienteCreate(nombre="Juan", apellido="Perez", email="juan@test.com")
        result = await service.create(data)

        assert result.id == 1
        assert result.email == "juan@test.com"

    async def test_create_duplicate_email(self, service, mock_repo):
        """WHEN creating with existing email THEN 422 is raised."""
        mock_repo.get_by_email.return_value = MagicMock()

        data = ClienteCreate(nombre="Juan", apellido="Perez", email="exists@test.com")
        with pytest.raises(HTTPException) as exc:
            await service.create(data)
        assert exc.value.status_code == 422
        assert "ya se encuentra registrado" in exc.value.detail


class TestClienteServiceGetAll:
    async def test_get_all_paginated(self, service, mock_repo):
        """WHEN getting all THEN paginated result is returned."""
        mock_repo.get_active.return_value = [
            Cliente(id=1, nombre="C1", apellido="U1", email="c1@test.com", activo=True),
        ]
        mock_repo.count_active.return_value = 1

        result = await service.get_all(page=1, size=20)

        assert result["total"] == 1
        assert len(result["items"]) == 1


class TestClienteServiceGetById:
    async def test_get_by_id_found(self, service, mock_repo):
        """WHEN getting existing cliente THEN it's returned."""
        mock_repo.get_by_id.return_value = Cliente(
            id=1, nombre="Juan", apellido="Perez",
            email="juan@test.com", activo=True,
        )
        result = await service.get_by_id(1)
        assert result.id == 1

    async def test_get_by_id_not_found(self, service, mock_repo):
        """WHEN getting non-existent cliente THEN 404."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(99999)
        assert exc.value.status_code == 404

    async def test_get_by_id_inactive(self, service, mock_repo):
        """WHEN getting inactive cliente THEN 404."""
        mock_repo.get_by_id.return_value = Cliente(
            id=2, nombre="Inactive", apellido="U",
            email="inactive@test.com", activo=False,
        )
        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(2)
        assert exc.value.status_code == 404


class TestClienteServiceUpdate:
    async def test_update_success(self, service, mock_repo):
        """WHEN updating valid cliente THEN it's updated."""
        existing = Cliente(id=1, nombre="Old", apellido="U", email="old@test.com", activo=True)
        mock_repo.get_by_id.return_value = existing
        mock_repo.get_by_email.return_value = None  # New email is unique
        mock_repo.update.return_value = Cliente(
            id=1, nombre="New", apellido="U", email="new@test.com", activo=True,
        )

        data = ClienteUpdate(nombre="New", email="new@test.com")
        result = await service.update(1, data)

        assert result.nombre == "New"

    async def test_update_not_found(self, service, mock_repo):
        """WHEN updating non-existent THEN 404."""
        mock_repo.get_by_id.return_value = None
        data = ClienteUpdate(nombre="New")
        with pytest.raises(HTTPException) as exc:
            await service.update(99999, data)
        assert exc.value.status_code == 404

    async def test_update_duplicate_email(self, service, mock_repo):
        """WHEN updating to existing email THEN 422."""
        existing = Cliente(id=1, nombre="Old", apellido="U", email="old@test.com", activo=True)
        mock_repo.get_by_id.return_value = existing
        mock_repo.get_by_email.return_value = MagicMock(id=2)

        data = ClienteUpdate(email="taken@test.com")
        with pytest.raises(HTTPException) as exc:
            await service.update(1, data)
        assert exc.value.status_code == 422


class TestClienteServiceDelete:
    async def test_delete_soft_delete(self, service, mock_repo):
        """WHEN deleting a cliente THEN it's soft-deleted."""
        existing = Cliente(id=1, nombre="Del", apellido="U", email="del@test.com", activo=True)
        mock_repo.get_by_id.return_value = existing

        await service.delete(1)

        assert existing.activo is False
        mock_repo.update.assert_called_once()

    async def test_delete_not_found(self, service, mock_repo):
        """WHEN deleting non-existent THEN 404."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.delete(99999)
        assert exc.value.status_code == 404
