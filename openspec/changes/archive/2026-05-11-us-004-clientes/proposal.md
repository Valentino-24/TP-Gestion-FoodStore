## Why

Actualmente el sistema no cuenta con una gestión formal de clientes/usuarios finales. Para registrar ventas, facturación, historial de compras y contacto personalizado, es necesario introducir una entidad "cliente" vinculada a pedidos y usuarios autenticados (rol CLIENT).

## What Changes

- Agregar modelo `Cliente` con campos principales: id, nombre, apellido, email, telefono, direccion, activo, creado_en, actualizado_en
- CRUD API REST para clientes en `/api/v1/clientes`
- Sólo usuarios rol ADMIN pueden crear, editar y borrar clientes; rol CLIENT puede consultar solo su propio registro
- Validaciones de email único y formato de datos básicos
- Migración Alembic para la tabla clientes
- Integración inicial (referencia) con pedidos/ordenes (para siguiente módulo)

## Capabilities

### New Capabilities
- `clientes`: Gestión de clientes finales — Alta, baja, modificación y consulta de clientes con seguridad y validaciones

### Modified Capabilities
- (ninguna, no existen requisitos cambiantes en módulos actuales)

## Impact

- Nuevos modelos y APIs en backend/app/clientes/
- Migración de base de datos (tabla clientes)
- Afecta sistemas de autenticación y relación con entidades futuras (pedidos, facturación)
- Requiere rol ADMIN y CLIENT en RBAC para rutas/seguridad
