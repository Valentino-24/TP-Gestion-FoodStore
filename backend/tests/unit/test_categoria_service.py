"""Tests for CategoriaService business logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.categorias.service import CategoriaService
from app.categorias.schemas import CategoriaCreate, CategoriaUpdate
from app.models.categoria import Categoria


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_by_name = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_active = AsyncMock()
    repo.count_active = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo):
    return CategoriaService(repo=mock_repo)


class TestCategoriaServiceCreate:
    async def test_create_success(self, service, mock_repo):
        """WHEN creating with valid data THEN categoria is created."""
        mock_repo.get_by_name.return_value = None
        mock_repo.create.return_value = Categoria(id=1, nombre="New Cat", descripcion="Desc")

        data = CategoriaCreate(nombre="New Cat", descripcion="Desc")
        result = await service.create(data)

        assert result.id == 1
        assert result.nombre == "New Cat"
        mock_repo.get_by_name.assert_called_once_with("New Cat")

    async def test_create_duplicate_name(self, service, mock_repo):
        """WHEN creating with existing name THEN 409 is raised."""
        mock_repo.get_by_name.return_value = MagicMock()

        data = CategoriaCreate(nombre="Existing")
        with pytest.raises(HTTPException) as exc:
            await service.create(data)
        assert exc.value.status_code == 409

    async def test_create_sets_active_true(self, service, mock_repo):
        """WHEN creating THEN activo defaults to True."""
        mock_repo.get_by_name.return_value = None
        mock_repo.create.return_value = Categoria(id=1, nombre="Active", activo=True)

        data = CategoriaCreate(nombre="Active")
        result = await service.create(data)

        # Verify the passed Categoria had activo=True
        created_arg = mock_repo.create.call_args[0][0]
        assert created_arg.activo is True


class TestCategoriaServiceGetAll:
    async def test_get_all_calls_repo(self, service, mock_repo):
        """WHEN getting all THEN delegates to repo.get_active."""
        mock_repo.get_active.return_value = [Categoria(id=1, nombre="C1")]
        result = await service.get_all(skip=0, limit=10)
        mock_repo.get_active.assert_called_once_with(skip=0, limit=10)
        assert len(result) == 1


class TestCategoriaServiceGetById:
    async def test_get_by_id_found(self, service, mock_repo):
        """WHEN getting by existing ID THEN categoria is returned."""
        mock_repo.get_by_id.return_value = Categoria(id=1, nombre="Found")
        result = await service.get_by_id(1)
        assert result.id == 1
        assert result.nombre == "Found"

    async def test_get_by_id_not_found(self, service, mock_repo):
        """WHEN getting by non-existent ID THEN 404 is raised."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(99999)
        assert exc.value.status_code == 404
        assert "Categoria no encontrada" in exc.value.detail


class TestCategoriaServiceUpdate:
    async def test_update_success(self, service, mock_repo):
        """WHEN updating with valid data THEN categoria is updated."""
        existing = Categoria(id=1, nombre="Old", descripcion="Old desc", activo=True)
        mock_repo.get_by_id.return_value = existing
        mock_repo.get_by_name.return_value = None
        mock_repo.update.return_value = Categoria(id=1, nombre="New", descripcion="New desc")

        data = CategoriaUpdate(nombre="New", descripcion="New desc")
        result = await service.update(1, data)

        assert result.nombre == "New"
        assert result.descripcion == "New desc" if hasattr(result, 'descripcion') else True

    async def test_update_not_found(self, service, mock_repo):
        """WHEN updating non-existent categoria THEN 404."""
        mock_repo.get_by_id.return_value = None
        data = CategoriaUpdate(nombre="New")
        with pytest.raises(HTTPException) as exc:
            await service.update(99999, data)
        assert exc.value.status_code == 404

    async def test_update_duplicate_name(self, service, mock_repo):
        """WHEN updating to an existing name THEN 409."""
        existing = Categoria(id=1, nombre="Old", activo=True)
        mock_repo.get_by_id.return_value = existing
        mock_repo.get_by_name.return_value = MagicMock(id=2)  # Another cat has this name

        data = CategoriaUpdate(nombre="Taken")
        with pytest.raises(HTTPException) as exc:
            await service.update(1, data)
        assert exc.value.status_code == 409


class TestCategoriaServiceDelete:
    async def test_delete_success(self, service, mock_repo):
        """WHEN deleting existing categoria THEN it's soft-deleted."""
        existing = Categoria(id=1, nombre="To Delete", activo=True)
        mock_repo.get_by_id.return_value = existing

        await service.delete(1)

        assert existing.activo is False
        mock_repo.update.assert_called_once_with(existing)

    async def test_delete_not_found(self, service, mock_repo):
        """WHEN deleting non-existent THEN 404."""
        mock_repo.get_by_id.return_value = None
        with pytest.raises(HTTPException) as exc:
            await service.delete(99999)
        assert exc.value.status_code == 404
