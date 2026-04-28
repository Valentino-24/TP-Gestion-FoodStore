## Why

El proyecto Food Store necesita una base sólida para comenzar a desarrollar. Sin infraestructura, no hay dónde implementar las features. Los docs definen FastAPI + SQLModel + PostgreSQL como stack, pero no existe código. Setup-infrastructure crea la fundación sobre la que se construye todo el sistema.

## What Changes

- FastAPI app entry point en `backend/app/main.py` con CORS y rate limiting
- Configuración centralizada con Pydantic Settings (`backend/app/config.py`)
- Database connection con SQLModel engine y session (`backend/app/database.py`)
- Core utilities: JWT/bcrypt security, pagination (`backend/app/core/`)
- Feature-first skeleton vacío en carpetas (auth/, usuarios/, categorias/, etc.)
- Alembic migrations configuradas
- Seed data para Roles y Estados (tablas catálogo)

## Capabilities

### New Capabilities

- **backend-app**: FastAPI application entry point con middlewares
- **database-connection**: SQLModel engine, AsyncSession, BaseRepository genérico
- **auth-dependencies**: get_current_user, require_role para FastAPI
- **seed-data**: Datos iniciales (Roles, Estados, FormasPago)

### Modified Capabilities

 Ninguno (es el primer change - no hay specs previas)

## Impact

- Backend: toda la estructura feature-first
- Dependencias Python: 13 paquetes en requirements.txt
- Database: PostgreSQL requerida
- Todos los changes futuros dependen de este