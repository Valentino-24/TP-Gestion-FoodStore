## Context

El proyecto tiene 3 componentes que corren de forma independiente:
- **PostgreSQL 16** — base de datos, requiere instalación manual
- **Backend** — FastAPI con Uvicorn en Python 3.12, requiere virtualenv + requirements.txt
- **Frontend** — Vite + React + TS en Node 22, requiere npm install

No existe una forma unificada de levantar el entorno. El desarrollador debe instalar y configurar cada componente por separado.

## Goals / Non-Goals

**Goals:**
- Un solo comando (`docker compose up`) que levante los 3 servicios
- Backend con hot-reload (uvicorn --reload) para desarrollo
- Frontend con hot-reload (Vite dev server)
- Migraciones Alembic ejecutadas automáticamente al iniciar el backend
- Seed data ejecutada automáticamente si la base está vacía
- Los archivos existentes de configuración (.env, requirements.txt, package.json) siguen siendo fuente de verdad

**Non-Goals:**
- Producción / deployment — es solo entorno de desarrollo local
- Docker image optimizadas para producción (multi-stage build, nginx, etc.)
- Cambiar la estructura del proyecto o archivos existentes
- CI/CD pipeline

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| Puerto frontend | 5173 (mismo que sin Docker) | Puerto diferente | Los .env y configs ya apuntan a 5173, evita conflictos mentales |
| Puerto backend | 8000 (mismo que sin Docker) | Puerto diferente | Misma razón — transparencia para el desarrollador |
| Base de datos | postgres:16 | Versión específica vs latest | PostgreSQL 16 es la versión usada actualmente, latest podría romper |
| Backend Dockerfile | python:3.12-slim | python:3.12 (full) | Slim reduce drásticamente el tamaño de la imagen |
| Hot-reload backend | Bind mount del código + uvicorn --reload | Copiar código en build | Bind mount permite hot-reload sin rebuild |
| Hot-reload frontend | Bind mount + vite dev | Build + nginx | Dev con hot-reload es más productivo |
| Seed data | Entrypoint script que corre seed_db.py | Init container, manual | Más simple, ejecuta solo si la base está vacía |

## Risks / Trade-offs

- [Riesgo] Bind mounts en Windows pueden tener problemas de rendimiento y watch → Usar WSL2 para Docker Desktop, o configurar polling en Vite
- [Riesgo] Puerto 5432 ocupado si el dev tiene PostgreSQL local → Documentar cómo cambiar el puerto en docker-compose o detener el PostgreSQL local
- [Riesgo] La seed data asume que la BD está vacía → El script seed_db.py debería ser idempotente o verificar antes de insertar
- [Trade-off] Usar `depends_on` sin `condition: service_healthy` puede causar race condition al arrancar → Usar `condition: service_healthy` y un healthcheck en PostgreSQL
