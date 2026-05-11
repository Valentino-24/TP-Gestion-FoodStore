## Why

El panel de administración existe como layout con rutas placeholder — todas apuntan al mismo componente `AdminDashboard` vacío. Los admins no pueden gestionar productos, categorías, clientes ni pedidos desde la interfaz web. Necesitan las herramientas CRUD y el dashboard con métricas para operar el sistema.

## What Changes

- Crear endpoint `GET /api/v1/admin/stats` con métricas del dashboard (pedidos hoy, ingresos hoy, total productos, total clientes activos)
- Reemplazar placeholder de Dashboard con cards de estadísticas en tiempo real
- Implementar página de gestión de productos: tabla con listado, búsqueda, edición inline o modal, y soft-delete
- Implementar página de gestión de categorías: tabla con CRUD completo (crear, editar, soft-delete)
- Implementar página de gestión de clientes: listado paginado con búsqueda y detalle
- Implementar página de gestión de pedidos: listado con filtros por estado, cambio de estado vía FSM (dropdown con transiciones válidas)

## Capabilities

### New Capabilities
- `admin-dashboard`: Dashboard de administración con cards de estadísticas (pedidos hoy, ingresos, productos, clientes) y endpoint backend `/admin/stats`
- `admin-panel`: Frontend de administración — páginas CRUD para productos, categorías, clientes y pedidos con gestión de estado FSM

### Modified Capabilities
<!-- No existing specs need modification — backend APIs ya soportan operaciones admin, solo falta el frontend -->

## Impact

- **Backend**: Nuevo endpoint `GET /api/v1/admin/stats` en módulo `admin/` (o integrado en módulos existentes)
- **Frontend**: 4 nuevas páginas admin (productos, categorías, clientes, pedidos) + dashboard con estadísticas
- **Router**: Ya tiene las rutas admin con placeholders — solo hay que reemplazar los componentes
- **Dependencias**: Ninguna nueva
