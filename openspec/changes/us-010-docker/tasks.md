## 1. Backend Dockerfile

- [x] 1.1 Create `backend/Dockerfile` basado en `python:3.12-slim`, con instalación de dependencias desde `requirements.txt`, healthcheck, y entrypoint que corre migraciones + seed + uvicorn --reload
- [x] 1.2 Create `backend/.dockerignore` excluyendo `__pycache__/`, `.venv/`, `.env`, `*.pyc`

## 2. Frontend Dockerfile

- [x] 2.1 Create `frontend/Dockerfile` basado en `node:22-alpine`, con instalación de dependencias y comando `npm run dev` con hot-reload
- [x] 2.2 Create `frontend/.dockerignore` excluyendo `node_modules/`, `dist/`, `.env`

## 3. Docker Compose

- [x] 3.1 Create `docker-compose.yml` con 3 servicios: `db` (postgres:16 con volume persistente y healthcheck), `api` (backend build con bind mount, depends_on db healthy, ports 8000, env vars), `frontend` (frontend build con bind mount, ports 5173, depends_on api)
- [x] 3.2 Configurar healthcheck en PostgreSQL y `condition: service_healthy` en el backend para evitar race conditions

## 4. Entrypoint Script

- [x] 4.1 Create `backend/docker-entrypoint.sh` que ejecute: `alembic upgrade head`, luego `python seed_db.py`, luego `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## 5. Verify

- [ ] 5.1 Verificar que `docker compose up --build` levanta los 3 servicios sin errores (requiere Docker instalado)
- [ ] 5.2 Verificar que la API responde en `http://localhost:8000/docs`
- [ ] 5.3 Verificar que el frontend responde en `http://localhost:5173`
- [ ] 5.4 Verificar que los datos persisten después de `docker compose down && docker compose up`
