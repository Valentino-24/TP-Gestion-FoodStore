"""Tests for ProductoService business logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.productos.service import ProductoService
from app.productos.schemas import ProductoCreate, ProductoUpdate
from app.models.producto import Producto


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_active = AsyncMock()
    repo.count_active = AsyncMock()
    return repo


@pytest.fixture
def mock_db():
    """Mock AsyncSession that returns a non-None categoria for validation."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=MagicMock())  # Categoria exists
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.fixture
def service(mock_repo, mock_db):
    return ProductoService(repo=mock_repo, db=mock_db)


class TestProductoServiceCreate:
    async def test_create_success(self, service, mock_repo):
        """WHEN creating with valid data THEN producto is created."""
        mock_repo.create.return_value = Producto(
            id=1, nombre="Test", precio=10.0, categoria_id=1, activo=True,
        )

        data = ProductoCreate(nombre="Test Product", precio=10.0, categoria_id=1)
        result = await service.create(data)

        assert result.id == 1
        assert result.nombre == "Test"
        mock_repo.create.assert_called_once()

    async def test_create_invalid_categoria(self, service, mock_db):
        """WHEN creating with invalid categoria_id THEN 404."""
        # Override mock_db to return None for categoria validation
        result = MagicMock()
        result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=result)

        data = ProductoCreate(nombre="Test", precio=10.0, categoria_id=99999)
        with pytest.raises(HTTPException) as exc:
            await service.create(data)
        assert exc.value.status_code == 404
        assert "Categoria no encontrada" in exc.value.detail


class TestProductoServiceGetAll:
    async def test_get_all_paginated(self, service, mock_repo):
        """WHEN getting all products THEN paginated dict is returned."""
        mock_repo.get_active.return_value = [
            Producto(id=1, nombre="P1", precio=10.0, categoria_id=1, activo=True),
        ]
        mock_repo.count_active.return_value = 1

        result = await service.get_all(page=1, size=20)

        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["page"] == 1
        assert result["size"] == 20

    async def test_get_all_with_category_filter(self, service, mock_repo):
        """WHEN filtering by categoria_id THEN repo is called with filter."""
        mock_repo.get_active.return_value = []
        mock_repo.count_active.return_value = 0

        await service.get_all(page=1, size=20, categoria_id=1)

        mock_repo.get_active.assert_called_once_with(skip=0, limit=20, categoria_id=1)
        mock_repo.count_active.assert_called_once_with(categoria_id=1)

    async def test_get_all_page_calculation(self, service, mock_repo):
        """WHEN requesting page 2 THEN skip is calculated correctly."""
        mock_repo.get_active.return_value = []
        mock_repo.count_active.return_value = 0

        await service.get_all(page=3, size=10)

        mock_repo.get_active.assert_called_once_with(skip=20, limit=10, categoria_id=None)


class TestProductoServiceGetById:
    async def test_get_by_id_found(self, service, mock_repo):
        """WHEN getting existing active product THEN it's returned."""
        mock_repo.get_by_id.return_value = Producto(
            id=1, nombre="P1", precio=10.0, categoria_id=1, activo=True,
        )
        result = await service.get_by_id(1)
        assert result.id == 1
        assert result.nombre == "P1"

    async def test_get_by_id_not_found(self, service, mock_repo):
        """WHEN getting non-existent product THEN 404."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(99999)
        assert exc.value.status_code == 404

    async def test_get_by_id_inactive(self, service, mock_repo):
        """WHEN getting inactive product THEN 404."""
        mock_repo.get_by_id.return_value = Producto(
            id=2, nombre="Inactive", precio=10.0, categoria_id=1, activo=False,
        )
        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(2)
        assert exc.value.status_code == 404


class TestProductoServiceUpdate:
    async def test_update_success(self, service, mock_repo):
        """WHEN updating with valid data THEN producto is updated."""
        existing = Producto(id=1, nombre="Old", precio=10.0, categoria_id=1, activo=True)
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = Producto(id=1, nombre="New", precio=15.0, categoria_id=1, activo=True)

        data = ProductoUpdate(nombre="New", precio=15.0)
        result = await service.update(1, data)

        assert result.nombre == "New"

    async def test_update_not_found(self, service, mock_repo):
        """WHEN updating non-existent product THEN 404."""
        mock_repo.get_by_id.return_value = None
        data = ProductoUpdate(nombre="New")
        with pytest.raises(HTTPException) as exc:
            await service.update(99999, data)
        assert exc.value.status_code == 404


class TestProductoServiceDelete:
    async def test_delete_soft_delete(self, service, mock_repo):
        """WHEN deleting a product THEN it's soft-deleted (activo=False)."""
        existing = Producto(id=1, nombre="To Delete", precio=10.0, categoria_id=1, activo=True)
        mock_repo.get_by_id.return_value = existing

        await service.delete(1)

        assert existing.activo is False
        mock_repo.update.assert_called_once_with(existing)

    async def test_delete_not_found(self, service, mock_repo):
        """WHEN deleting non-existent product THEN 404."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.delete(99999)
        assert exc.value.status_code == 404
