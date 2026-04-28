## 1. Backend App Structure

- [x] 1.1 Create `backend/app/__init__.py`
- [x] 1.2 Create `backend/app/main.py` with FastAPI app, CORS middleware, rate limiting
- [x] 1.3 Create `backend/app/config.py` with Pydantic Settings from .env

## 2. Core Utilities

- [x] 2.1 Create `backend/app/core/__init__.py`
- [x] 2.2 Create `backend/app/core/security.py` (JWT, bcrypt helpers)
- [x] 2.3 Create `backend/app/core/pagination.py` (paginate response helper)

## 3. Database Layer

- [x] 3.1 Create `backend/app/database.py` (SQLModel engine, async_session_maker)
- [x] 3.2 Create `backend/app/repositories/__init__.py`
- [x] 3.3 Create `backend/app/repositories/base.py` (BaseRepository generic)
- [x] 3.4 Create `backend/app/unit_of_work.py` (Unit of Work context manager)

## 4. Auth Dependencies

- [x] 4.1 Create `backend/app/dependencies.py` (get_db, get_current_user, require_role)

## 5. Feature Module Skeleton

- [x] 5.1 Create `backend/app/auth/__init__.py`, `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
- [x] 5.2 Create `backend/app/usuarios/__init__.py`, skeleton files
- [x] 5.3 Create `backend/app/categorias/__init__.py`, skeleton files
- [x] 5.4 Create `backend/app/productos/__init__.py`, skeleton files
- [x] 5.5 Create `backend/app/pedidos/__init__.py`, skeleton files
- [x] 5.6 Create `backend/app/pagos/__init__.py`, skeleton files
- [x] 5.7 Create `backend/app/direcciones/__init__.py`, skeleton files
- [x] 5.8 Create `backend/app/admin/__init__.py`, skeleton files
- [x] 5.9 Create `backend/app/refreshtokens/__init__.py`, skeleton files

## 6. Database Seed

- [x] 6.1 Create `backend/app/db/__init__.py`
- [x] 6.2 Create `backend/app/db/seed.py` with idempotent seed for Roles
- [x] 6.3 Create `backend/app/db/seed.py` with idempotent seed for EstadoPedido
- [x] 6.4 Create `backend/app/db/seed.py` with idempotent seed for FormaPago
- [x] 6.5 Run seed script and verify data inserted

## 7. Alembic Setup

- [x] 7.1 Create `backend/alembic.ini` basic config
- [x] 7.2 Create `backend/migrations/env.py`
- [x] 7.3 Create `backend/migrations/script.py.mako`

## 8. Verification

- [x] 8.1 Run `uvicorn app.main:app --reload` and verify starts
- [x] 8.2 Access http://localhost:8000/docs - Swagger loads
- [x] 8.3 Access http://localhost:8000/redoc - ReDoc loads
- [x] 8.4 Verify CORS allows frontend origin
- [x] 8.5 Verify seed data in database (SELECT * FROM rol)