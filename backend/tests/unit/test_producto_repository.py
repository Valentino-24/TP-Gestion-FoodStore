"""Tests for ProductoRepository custom queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.productos.repository import ProductoRepository
from app.models.producto import Producto


@pytest.fixture
def repo(db_session: AsyncSession) -> ProductoRepository:
    return ProductoRepository(db_session)


@pytest.fixture
async def sample_categoria(db_session: AsyncSession) -> int:
    from app.models.categoria import Categoria
    cat = Categoria(nombre="Test Cat for Products")
    db_session.add(cat)
    await db_session.flush()
    return cat.id


class TestProductoRepositoryGetActive:
    async def test_get_active_only_active(self, repo, db_session, sample_categoria):
        """WHEN getting active products THEN only active ones are returned."""
        p1 = Producto(nombre="Active", precio=10, categoria_id=sample_categoria, activo=True)
        p2 = Producto(nombre="Inactive", precio=10, categoria_id=sample_categoria, activo=False)
        db_session.add_all([p1, p2])
        await db_session.flush()
        active = await repo.get_active()
        names = [p.nombre for p in active]
        assert "Active" in names
        assert "Inactive" not in names

    async def test_get_active_filter_by_categoria(self, repo, db_session, sample_categoria):
        """WHEN filtering by categoria_id THEN only matching products are returned."""
        from app.models.categoria import Categoria
        cat2 = Categoria(nombre="Second Category")
        db_session.add(cat2)
        await db_session.flush()

        p1 = Producto(nombre="In Cat1", precio=10, categoria_id=sample_categoria, activo=True)
        p2 = Producto(nombre="In Cat2", precio=10, categoria_id=cat2.id, activo=True)
        db_session.add_all([p1, p2])
        await db_session.flush()

        filtered = await repo.get_active(categoria_id=sample_categoria)
        assert len(filtered) == 1
        assert filtered[0].nombre == "In Cat1"

    async def test_get_active_ordered_by_name(self, repo, db_session, sample_categoria):
        """WHEN getting active products THEN they are ordered by name."""
        p_z = Producto(nombre="Zebra", precio=10, categoria_id=sample_categoria, activo=True)
        p_a = Producto(nombre="Alpha", precio=10, categoria_id=sample_categoria, activo=True)
        db_session.add_all([p_z, p_a])
        await db_session.flush()
        active = await repo.get_active()
        # Alpha should come before Zebra
        alpha_idx = next(i for i, p in enumerate(active) if p.nombre == "Alpha")
        zebra_idx = next(i for i, p in enumerate(active) if p.nombre == "Zebra")
        assert alpha_idx < zebra_idx

    async def test_get_active_pagination(self, repo, db_session, sample_categoria):
        """WHEN getting active with pagination THEN correct pages."""
        for i in range(5):
            db_session.add(Producto(nombre=f"Prod {i}", precio=i * 10, categoria_id=sample_categoria, activo=True))
        await db_session.flush()
        page1 = await repo.get_active(skip=0, limit=2)
        page2 = await repo.get_active(skip=2, limit=2)
        assert len(page1) == 2
        assert len(page2) == 2
        # Verify no overlap
        ids_page1 = {p.id for p in page1}
        ids_page2 = {p.id for p in page2}
        assert ids_page1.isdisjoint(ids_page2)


class TestProductoRepositoryCountActive:
    async def test_count_active_all(self, repo, db_session, sample_categoria):
        """WHEN counting active products THEN correct total."""
        for i in range(3):
            db_session.add(Producto(nombre=f"P{i}", precio=10, categoria_id=sample_categoria, activo=True))
        await db_session.flush()
        assert await repo.count_active() == 3

    async def test_count_active_filtered(self, repo, db_session, sample_categoria):
        """WHEN counting active with categoria filter THEN correct filtered count."""
        from app.models.categoria import Categoria
        cat2 = Categoria(nombre="Cat Filter Count")
        db_session.add(cat2)
        await db_session.flush()
        db_session.add(Producto(nombre="P1", precio=10, categoria_id=sample_categoria, activo=True))
        db_session.add(Producto(nombre="P2", precio=10, categoria_id=cat2.id, activo=True))
        await db_session.flush()
        assert await repo.count_active(categoria_id=sample_categoria) == 1
        assert await repo.count_active(categoria_id=cat2.id) == 1


class TestProductoRepositoryGetById:
    async def test_get_by_id_includes_inactive(self, repo, db_session, sample_categoria):
        """WHEN getting by ID THEN inactive products are also returned."""
        p = Producto(nombre="Hidden", precio=10, categoria_id=sample_categoria, activo=False)
        db_session.add(p)
        await db_session.flush()
        found = await repo.get_by_id(p.id)
        assert found is not None
        assert found.activo is False
