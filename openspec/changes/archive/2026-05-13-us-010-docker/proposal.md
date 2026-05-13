## Why

El proyecto actualmente requiere que el desarrollador instale PostgreSQL, Python con virtualenv, y Node.js manualmente. No hay una forma estandarizada de levantar el entorno completo con un solo comando, lo que dificulta el onboarding y la consistencia entre entornos de desarrollo.

## What Changes

- **Docker Compose** con 3 servicios: PostgreSQL 16, API backend (FastAPI + Uvicorn), Frontend (Vite dev server)
- **Dockerfile para backend** basado en Python 3.12 slim, con dependencias desde requirements.txt
- **Dockerfile para frontend** basado en Node 22 para dev con hot-reload
- **.dockerignore** para backend y frontend
- Scripts de inicialización: migraciones Alembic + seed data al arrancar el backend
- Variables de entorno centralizadas en el docker-compose

## Capabilities

### New Capabilities
- `docker-setup`: Entorno de desarrollo local con Docker Compose — 3 servicios (PostgreSQL, API, Frontend) listos con un solo comando

### Modified Capabilities
<!-- No existing specs change — docker-setup es infraestructura, no modifica requerimientos de funcionalidad existente -->

## Impact

- **Nuevos archivos**: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/.dockerignore`, `frontend/.dockerignore`
- **No rompe el flujo existente**: el desarrollo sin Docker sigue funcionando igual
- **Variables de entorno**: se pasan vía docker-compose, con valores por defecto para desarrollo local
- **Seed data**: se ejecuta automáticamente al iniciar el backend si la base está vacía
