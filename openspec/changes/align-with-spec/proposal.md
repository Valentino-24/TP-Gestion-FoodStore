## Why

El proyecto está implementado pero tiene una brecha significativa con la especificación técnica v5.0 (Integrador.txt). La rúbrica de 200 puntos evalúa items como TanStack Query, 4 stores Zustand, recharts, Feature-Sliced Design, HistorialEstadoPedido, snapshot pattern y stock management que no están implementados o están incompletos. Sin estos cambios, el proyecto pierde puntos en la corrección.

## What Changes

- **TanStack Query**: Instalar `@tanstack/react-query` y migrar todas las llamadas API de `useEffect` a hooks con `useQuery`/`useMutation`, con queryKeys descriptivos e invalidación automática
- **4 Zustand stores**: Implementar `paymentStore` (estado del proceso de pago) y `uiStore` (tema, sidebar, toasts) para completar los 4 stores que exige la especificación
- **recharts en dashboard**: Reemplazar las cards planas del admin dashboard con gráficos de barras/líneas (ingresos semanales, pedidos por estado, top productos)
- **HistorialEstadoPedido**: Implementar modelo, repository, y registro append-only de cada transición de estado del pedido
- **Snapshot pattern**: Al crear un pedido, capturar `precio_snapshot` en cada detalle y `direccion_snapshot` en el pedido para garantizar inmutabilidad histórica
- **Stock management**: Decrementar stock atómicamente al confirmar pedido, restaurar al cancelar
- **Feature-Sliced Design**: Reorganizar la estructura del frontend hacia pages/features/entities/shared con límites de importación claros
- **Error handling**: Implementar manejo de errores RFC 7807 en backend + error boundary y toasts en frontend

## Capabilities

### New Capabilities
- `backend-testing`: Already exists — expandir tests para cubrir HistorialEstadoPedido, stock, snapshots
- `admin-dashboard`: Already exists — agregar gráficos recharts

### Modified Capabilities
- `shopping-cart`: Migrar fetching de productos/pedidos de useEffect a TanStack Query
- `pedidos-api`: Agregar HistorialEstadoPedido, snapshot pattern, stock decrement/restore
- `frontend-base`: Agregar paymentStore, uiStore, error boundary global
- `admin-panel`: Dashboard con recharts en lugar de cards planas

## Impact

- **Backend**: `app/models/historial_estado.py` (nuevo), `app/pedidos/service.py` (registrar historial, snapshots, stock), `app/pedidos/schemas.py` (snapshots en responses)
- **Frontend**: Instalar `@tanstack/react-query`, `recharts`. Refactor de `stores/` (agregar paymentStore, uiStore). Refactor de hooks API a TanStack Query. Nuevos componentes de gráficos en admin. Error boundary global
- **Dependencias nuevas**: `@tanstack/react-query`, `recharts` (npm)
- **Breaking**: Migración de `useEffect` + axios directo a TanStack Query — cambios en varios componentes
