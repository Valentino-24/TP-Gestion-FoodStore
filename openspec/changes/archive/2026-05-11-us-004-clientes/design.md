## Context

Actualmente el sistema sólo maneja usuarios para autenticación y acceso (rol CLIENT incluido), pero no existe una entidad específica cliente con datos de contacto y perfil. Pedidos y facturación futuros requerirán vincular información relacional más rica. El backend es FastAPI con SQLModel, patrones de repository/service/router, y RBAC con JWT.

## Goals / Non-Goals

**Goals:**
- Modelo Cliente completo, separado de usuario authentication
- REST API para CRUD clientes bajo /api/v1/clientes
- Validaciones de integridad y unicidad (email)
- Seguridad en endpoints según rol (ADMIN, CLIENT)
- Sentar base para vinculación futura con pedidos/ordenes

**Non-Goals:**
- Autenticación propia de clientes (usa usuarios/auth existente)
- Integración “full” con pedidos/ordenes (sólo referencia inicial)
- Funcionalidad de facturación o direcciones múltiples

## Decisions

- Cliente es entidad distinta de User (User: auth/credencial; Cliente: datos personales, contacto, lógica de negocio)
- Un email sólo puede existir una vez en clientes (unicidad estricta)
- Rol ADMIN puede crear/edit/borrar cualquier cliente; rol CLIENT sólo ve el suyo
- Repository/service/router igual que productos/categorias
- Seeding inicial igual a productos, estructura en backend/app/clientes/
- SQLModel + Alembic migration, relación 1:N con pedidos (futura)

## Risks / Trade-offs

- [Risk] Duplicar datos con usuarios → Mitigado vinculando (más adelante) Cliente a UserID (para trazabilidad)
- [Risk] Rol CLIENT acceda a datos ajenos → Apis filtran por user vinculado o ID propio; tests vía specs
- [Risk] Email no validado → Se implementarán validadores de formato, unicidad y longitud
