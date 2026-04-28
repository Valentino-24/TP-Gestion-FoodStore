## Context

El proyecto Food Store necesita基础设施 base para comenzar. Stack definido en docs:
- Backend: FastAPI + SQLModel + PostgreSQL
- Arquitectura: Router → Service → UoW → Repository → Model (feature-first)

No existe código escrito. Solo docs, requirements.txt (actualizado), y configuración.

## Goals / Non-Goals

**Goals:**
- FastAPI app corriendo con `backend/app/main.py`
- Database connection funcionando con SQLModel
- Auth dependencies (JWT, RBAC) inyectables
- Seed data ejecutable para catálogos base
- Estructura feature-first creada (carpetas vacías)

**Non-Goals:**
- No implementar auth endpoints (próximo change: auth-system)
- No crear modelos de dominio (se CREAN aquí la Base y genéricos)
- No crear admin user - se hace a mano después
- Alembic migrations para tablas (no hay modelos de negocio aún)

## Decisions

### D1: main.py en backend/app/
**Decision**: Ubicar main.py en `backend/app/main.py` (no raíz)
**Rationale**: Conveniencia del imports. Permite `from app import config` clean.agregan ventajas para luego, `import app.main`.user prefirió esta ubicación.

**Alternativas consideradas**:
- Raíz (`backend/main.py`): Import conflicts, no escalable

### D2: SQLModel async
**Decision**: Usar SQLModel async (AsyncSession) con asyncpg
**Rationale**: FastAPI es async-native. Docs lo confirman.

**Alternativas consideradas**:
- Sync: Contrario al docs stack, blocking

### D3: Feature-first vacío
**Decision**: Crear carpetas vacías (auth/, usuarios/, etc.) como skeleton
**Rationale**: Cada módulo tendrá 5 archivos. Mejor crear estructura ahora que después.

**Alternativas consideradas**:
- Solo app core: No sigue la arquitectura feature-first del docs

### D4: Alembic sin migraciones
**Decision**: Alembic CONFIGURADO pero SIN migraciones iniciales
**Rationale**: No hay modelos definidos. Se configura para futuro cuando hayan modelos con clases SQLModel(tabla=True).

**Alternativas consideradas**:
- Migración vacía: No existe Base.metadata para migrar

### D5: Seed idempotente
**Decision**: Usar `INSERT ... ON CONFLICT DO NOTHING`
**Rationale**: Devs ejecutarán múltiples veces. No duplicar.

## Risks / Trade-offs

- **[Risk]** PostgreSQL no disponible → **Mitigation**: docs dice PostgreSQL requerido, indicar en .env que se necesita
- **[Risk]** Python version → **Mitigation**: Requiere 3.11+, verificar antes de pip install
- **[Risk]** Circular imports (app → config → settings → app) → **Mitigation**: usar lazy imports o pasar settings como dependencia

## Migration Plan

```bash
# Nuevo developer steps:
cd backend
cp .env.example .env
# [CONFIGURAR DATABASE_URL]

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
# Access: http://localhost:8000/docs
```

**Rollback**: Eliminar `.venv` y recreate.

## Open Questions

1. **Q**: ¿Cuántos feature modules crear ahora?  
   **A**: Solo los principales (auth, usuarios, categorias, productos, pedidos, pagos, direcciones) - no todos los 9

2. **Q**: ¿Scripts de seed van en app/ o en scripts/?  
   **A**: `backend/app/db/` convention, seed.py dentro

3. **Q**: migrations/ versiones se generan automatic?  
   **A**: No hasta tener modelos SQLModel(tabla=True)