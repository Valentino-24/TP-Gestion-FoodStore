"""Tests for CategoriaRepository custom queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.categorias.repository import CategoriaRepository
from app.models.categoria import Categoria


@pytest.fixture
def repo(db_session: AsyncSession) -> CategoriaRepository:
    return CategoriaRepository(db_session)


class TestCategoriaRepositoryGetByName:
    async def test_get_by_name_found(self, repo, db_session):
        """WHEN searching by name that exists THEN category is returned."""
        cat = Categoria(nombre="Unique Cat Name", descripcion="Test")
        db_session.add(cat)
        await db_session.flush()
        found = await repo.get_by_name("Unique Cat Name")
        assert found is not None
        assert found.nombre == "Unique Cat Name"

    async def test_get_by_name_case_insensitive(self, repo, db_session):
        """WHEN searching with different case THEN category is found."""
        cat = Categoria(nombre="UpperCase", descripcion="Test")
        db_session.add(cat)
        await db_session.flush()
        found = await repo.get_by_name("uppercase")
        assert found is not None
        assert found.nombre == "UpperCase"

    async def test_get_by_name_not_found(self, repo):
        """WHEN searching by non-existent name THEN None is returned."""
        found = await repo.get_by_name("NonExistentName")
        assert found is None


class TestCategoriaRepositoryGetActive:
    async def test_get_active_only_active(self, repo, db_session):
        """WHEN getting active categories THEN only active ones are returned."""
        cat1 = Categoria(nombre="Active 1", activo=True)
        cat2 = Categoria(nombre="Inactive", activo=False)
        cat3 = Categoria(nombre="Active 2", activo=True)
        db_session.add_all([cat1, cat2, cat3])
        await db_session.flush()
        active = await repo.get_active()
        names = [c.nombre for c in active]
        assert "Active 1" in names
        assert "Active 2" in names
        assert "Inactive" not in names

    async def test_get_active_ordered_by_name(self, repo, db_session):
        """WHEN getting active categories THEN they are ordered by name."""
        cat_a = Categoria(nombre="Zebra", activo=True)
        cat_b = Categoria(nombre="Alpha", activo=True)
        db_session.add_all([cat_a, cat_b])
        await db_session.flush()
        active = await repo.get_active()
        names = [c.nombre for c in active]
        # Last two should be Alpha, Zebra
        assert names[-2:] == ["Alpha", "Zebra"] or names == ["Alpha", "Zebra"]

    async def test_get_active_pagination(self, repo, db_session):
        """WHEN getting active with skip/limit THEN pagination works."""
        for i in range(5):
            db_session.add(Categoria(nombre=f"PageActive {i}", activo=True))
        await db_session.flush()
        page1 = await repo.get_active(skip=0, limit=2)
        page2 = await repo.get_active(skip=2, limit=2)
        assert len(page1) == 2
        assert len(page2) == 2


class TestCategoriaRepositoryCountActive:
    async def test_count_active_only_active(self, repo, db_session):
        """WHEN counting active categories THEN only active are counted."""
        db_session.add(Categoria(nombre="A1", activo=True))
        db_session.add(Categoria(nombre="A2", activo=True))
        db_session.add(Categoria(nombre="Inactive", activo=False))
        await db_session.flush()
        count = await repo.count_active()
        assert count == 2
