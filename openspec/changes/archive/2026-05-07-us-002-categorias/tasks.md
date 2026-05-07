## 1. Model & Migration

- [x] 1.1 Create `backend/app/models/categoria.py` — Categoria model with id, nombre (unique, indexed), descripcion, activo (default True), creado_en, actualizado_en
- [x] 1.2 Register Categoria in `backend/app/models/__init__.py` export
- [x] 1.3 Generate Alembic migration for categoria table
- [x] 1.4 Verify migration runs cleanly with `alembic upgrade head`

## 2. Pydantic Schemas

- [x] 2.1 Create `backend/app/categorias/schemas.py` — CategoriaCreate (nombre, descripcion opcional), CategoriaUpdate (nombre, descripcion, activo opcionales), CategoriaResponse (id, nombre, descripcion, activo, creado_en, actualizado_en)

## 3. Repository

- [x] 3.1 Create `backend/app/categorias/repository.py` — CategoriaRepository extending BaseRepository[Categoria] with get_by_name (for duplicate check), get_active (filter activo=true)

## 4. Service

- [x] 4.1 Create `backend/app/categorias/service.py` — CategoriaService with create (validate unique name, auto activo=true), get_all (active only, ordered), get_by_id, update (validate unique name), delete (soft delete via activo=false)

## 5. Router

- [x] 5.1 Implement `backend/app/categorias/router.py` — POST /categorias (admin-only create), GET /categorias (auth list), GET /categorias/{id} (auth detail), PUT /categorias/{id} (admin-only update), DELETE /categorias/{id} (admin-only soft delete)
- [x] 5.2 Register router in `backend/app/main.py`

## 6. Seed Data

- [x] 6.1 Add initial categories to seed script: Bebidas, Comidas, Snacks, Postres, Otros
- [x] 6.2 Run seed and verify categories in DB

## 7. Verification

- [x] 7.1 Verify GET /api/v1/categorias returns 200 with category list (authenticated)
- [x] 7.2 Verify GET /api/v1/categorias returns 401 without token
- [x] 7.3 Verify POST /api/v1/categorias creates category (admin)
- [x] 7.4 Verify POST /api/v1/categorias returns 403 for non-admin
- [x] 7.5 Verify POST /api/v1/categorias returns 409 on duplicate name
- [x] 7.6 Verify GET /api/v1/categorias/{id} returns category detail
- [x] 7.7 Verify GET /api/v1/categorias/{id} returns 404 for missing
- [x] 7.8 Verify PUT /api/v1/categorias/{id} updates category
- [x] 7.9 Verify DELETE /api/v1/categorias/{id} soft-deletes (activo=false)
- [x] 7.10 Verify seed categories are present and accessible
