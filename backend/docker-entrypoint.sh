#!/bin/sh
set -e

echo "Creating seed tables (rol, estado_pedido, forma_pago)..."
python docker_pre_migrate.py

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running seed data..."
python seed_db.py

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
