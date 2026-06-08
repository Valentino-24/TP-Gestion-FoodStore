## Why

El panel de administración actual tiene funcionalidad básica: dashboard con 4 cards de métricas, CRUD de productos/categorías, listado de clientes y gestión básica de pedidos. Faltan features clave como CRUD de usuarios con asignación de roles, dashboard con gráficos, gestión de stock, y modales de confirmación. Esto limita la utilidad del panel y no cubre la especificación completa.

## What Changes

- **CRUD de usuarios**: Listar, crear, editar y desactivar usuarios desde el panel admin. Asignar roles (ADMIN, STOCK, PEDIDOS, CLIENT)
- **Dashboard con recharts**: Gráficos de ingresos semanales, pedidos por estado (torta), top 5 productos más vendidos (barras)
- **Gestión de stock desde admin**: Campo editable de stock en la tabla de productos, con botón para actualizar cantidad
- **Modales de confirmación**: Antes de eliminar/desactivar cualquier entidad, mostrar modal de confirmación
- **Filtros avanzados en pedidos**: Filtrar por rango de fechas, estado, y búsqueda por ID de pedido
- **Exportación**: Botón para exportar listados a CSV (productos, pedidos, clientes)

## Capabilities

### New Capabilities
- `user-management-admin-ui`: CRUD de usuarios con asignación de roles desde el panel admin
- `data-export`: Exportación de listados a CSV desde el panel admin

### Modified Capabilities
- `admin-panel`: Dashboard con recharts, gestión de stock inline, modales de confirmación, filtros avanzados en pedidos

## Impact

- **Backend**: Endpoints admin para CRUD de usuarios con asignación de roles. Endpoint de exportación CSV. Endpoint PATCH de stock
- **Frontend**: Nuevas páginas `admin/UsuariosAdminPage.tsx`, componente `ConfirmModal.tsx`. Modificar `AdminDashboard.tsx` (recharts), `ProductosAdminPage.tsx` (stock inline), `PedidosAdminPage.tsx` (filtros avanzados)
- **Dependencias nuevas**: `recharts` (npm), posiblemente `papaparse` o similar para CSV
