## Why

La máquina de estados del pedido (FSM) es el dominio central del sistema según la especificación, pero está incompleta. No existe HistorialEstadoPedido (audit trail append-only), el stock no se decrementa/restaura atómicamente al confirmar/cancelar, y el cliente no puede cancelar sus propios pedidos. Sin esto, la trazabilidad y la integridad del inventario no están garantizadas.

## What Changes

- **HistorialEstadoPedido**: Modelo SQLModel con id, pedido_id (FK), estado_desde, estado_hasta, usuario_id (nullable para sistema), observacion, creado_en. Append-only: solo INSERT, nunca UPDATE/DELETE
- **Registro automático**: Cada transición de estado registra un entry en el historial con timestamp y usuario responsable
- **Stock decrement atómico**: Al transicionar PENDIENTE → CONFIRMADO, decrementar stock_cantidad de cada producto dentro de la misma transacción UoW
- **Stock restore atómico**: Al cancelar un pedido CONFIRMADO, restaurar el stock de todos los productos
- **Cancelación por CLIENTE**: El cliente puede cancelar su propio pedido solo si está en PENDIENTE (endpoint PATCH /api/v1/pedidos/{id}/cancelar)
- **Frontend timeline**: Visualización del historial de estados en la página de detalle del pedido (timeline vertical)
- **Frontend cancelación**: Botón "Cancelar pedido" en detalle del pedido para pedidos en PENDIENTE

## Capabilities

### New Capabilities
- `order-timeline`: Componente frontend de timeline visual del historial de estados del pedido

### Modified Capabilities
- `pedidos-api`: Agregar HistorialEstadoPedido, stock decrement/restore, endpoint de cancelación por CLIENTE
- `orders-history`: Agregar timeline visual en OrderDetailPage, botón de cancelación en pedidos PENDIENTE
- `admin-panel`: Gestión de pedidos con transiciones de estado completas (incluyendo CONFIRMADO manual para Efectivo)

## Impact

- **Backend**: Nuevo modelo `app/models/historial_estado.py`. Modificar `app/pedidos/service.py` (registrar historial, stock ops). Modificar `app/pedidos/router.py` (nuevo endpoint cancelar). Modificar `app/productos/repository.py` (stock update atómico)
- **Frontend**: Modificar `OrderDetailPage.tsx` (timeline + cancel button). Modificar `PedidosAdminPage.tsx` (transiciones completas)
- **Migración**: Nueva tabla `historial_estado_pedido` vía Alembic
- **Dependencias nuevas**: Ninguna
