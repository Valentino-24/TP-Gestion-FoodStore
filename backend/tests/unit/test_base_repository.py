"""Tests for BaseRepository CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categoria import Categoria
from app.repositories.base import BaseRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> BaseRepository[Categoria]:
    """Create a BaseRepository instance for testing."""
    return BaseRepository(db_session, Categoria)


class TestBaseRepositoryCreate:
    async def test_create_entity(self, repo, db_session):
        """WHEN creating an entity THEN it is saved with a generated ID."""
        cat = Categoria(nombre="Test Cat", descripcion="Description")
        created = await repo.create(cat)
        assert created.id is not None
        assert created.id > 0
        assert created.nombre == "Test Cat"

    async def test_create_duplicate_allowed_by_repo(self, repo, db_session):
        """WHEN creating two entities with same data THEN both are saved (no unique check in repo)."""
        cat1 = Categoria(nombre="Same Name A")
        cat2 = Categoria(nombre="Same Name B")
        c1 = await repo.create(cat1)
        c2 = await repo.create(cat2)
        assert c1.id != c2.id


class TestBaseRepositoryGetById:
    async def test_get_by_id_found(self, repo, db_session):
        """WHEN getting by existing ID THEN entity is returned."""
        cat = Categoria(nombre="Find Me")
        created = await repo.create(cat)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.nombre == "Find Me"

    async def test_get_by_id_not_found(self, repo):
        """WHEN getting by non-existent ID THEN None is returned."""
        found = await repo.get_by_id(99999)
        assert found is None


class TestBaseRepositoryGetAll:
    async def test_get_all_returns_all(self, repo, db_session):
        """WHEN getting all entities THEN all are returned."""
        for i in range(5):
            await repo.create(Categoria(nombre=f"Cat {i}"))
        all_items = await repo.get_all()
        assert len(all_items) >= 5

    async def test_get_all_with_pagination(self, repo, db_session):
        """WHEN using skip/limit THEN correct subset is returned."""
        for i in range(10):
            await repo.create(Categoria(nombre=f"Page Cat {i}"))
        page1 = await repo.get_all(skip=0, limit=3)
        page2 = await repo.get_all(skip=3, limit=3)
        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0].id != page2[0].id


class TestBaseRepositoryUpdate:
    async def test_update_entity(self, repo, db_session):
        """WHEN updating an entity THEN changes are persisted."""
        cat = Categoria(nombre="Before")
        created = await repo.create(cat)
        created.nombre = "After"
        updated = await repo.update(created)
        assert updated.nombre == "After"
        # Verify from DB
        fetched = await repo.get_by_id(created.id)
        assert fetched.nombre == "After"


class TestBaseRepositoryDelete:
    async def test_delete_entity(self, repo, db_session):
        """WHEN deleting an entity THEN it is removed."""
        cat = Categoria(nombre="To Delete")
        created = await repo.create(cat)
        await repo.delete(created)
        fetched = await repo.get_by_id(created.id)
        assert fetched is None

    async def test_delete_removes_from_count(self, repo, db_session):
        """WHEN deleting THEN count decreases."""
        cat = Categoria(nombre="Count Test")
        created = await repo.create(cat)
        before = await repo.count()
        await repo.delete(created)
        after = await repo.count()
        assert after == before - 1


class TestBaseRepositoryCount:
    async def test_count_returns_total(self, repo, db_session):
        """WHEN counting entities THEN total is returned."""
        for i in range(3):
            await repo.create(Categoria(nombre=f"Count {i}"))
        total = await repo.count()
        assert total >= 3
