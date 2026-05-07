## Context

The FoodStore backend has auth (us-001) complete with JWT-based authentication and role-based access control (RBAC) using ADMIN, STOCK, PEDIDOS, CLIENT roles. The categorias module is the first domain CRUD module. Current app structure uses SQLModel + SQLAlchemy async, BaseRepository pattern for DB operations, and Pydantic schemas for validation. All categoria stubs exist under `backend/app/categorias/`.

## Goals / Non-Goals

**Goals:**
- Categoria model with id, nombre (unique, indexed), descripcion, activo
- Full CRUD REST API at `/api/v1/categorias`
- Admin-only write (POST, PUT, DELETE); authenticated users read (GET)
- Soft delete via `activo = false` flag (not physical row removal)
- Alembic migration for the categoria table
- Initial seed data for common categories

**Non-Goals:**
- Product integration (us-003-productos will add FK to categoria)
- Pagination (simple list for now, pagination can be added later via core/pagination.py pattern)
- Hierarchical/nested categories (flat structure only)
- File uploads (images, icons for categories)
- Role-based visibility filtering

## Decisions

| Decision | Choice | Rationale | Alternatives |
|----------|--------|-----------|-------------|
| Soft delete via `activo` flag | `activo: bool = True` | Products will reference categoria_id — hard delete would orphan products. Soft delete keeps referential integrity. | Hard delete |
| Repository | Direct `BaseRepository[Categoria]` in categorias/repository.py | Consistent with auth module pattern. No need for custom queries on a simple CRUD. | Inline in service |
| Service layer | `CategoriaService` in categorias/service.py | Keeps business logic (soft-delete filter, admin-only checks) out of router. Consistent with auth pattern. | Logic in router |
| Model location | `app/models/categoria.py` with registration in `app/models/__init__.py` | All models in one place for Alembic auto-detection. Consistent with existing models. | In-module model |
| Admin write check | `require_role("ADMIN")` dependency from auth | Reuses existing RBAC. No need for custom permission logic. | Custom middleware |
| Unique constraint | DB-level unique on nombre + application-level validation | Prevents duplicate categories at DB level with clean 409 response at API level. | App-level only |

## Risks / Trade-offs

- [Risk] Deleting a category with linked products → Mitigated by soft delete (activo=false). Products module can filter by activo categories.
- [Risk] Category list grows unbounded → Low risk (categories are finite), but pagination can be added later via `core/pagination.py`.
- [Trade-off] Flat category structure → Simple and sufficient for food store needs. Hierarchical would add complexity without clear benefit.
