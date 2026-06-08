## 1. TanStack Query — Instalación y configuración base

- [ ] 1.1 Instalar `@tanstack/react-query` v5 en frontend
- [ ] 1.2 Crear `QueryClientProvider` en `App.tsx` con configuración base (staleTime, retry, refetchOnWindowFocus)
- [ ] 1.3 Crear directorios de estructura destino: `src/entities/`, `src/entities/producto/`, `src/entities/pedido/`, `src/entities/auth/`, `src/shared/ui/`, `src/shared/api/`, `src/shared/types/`, `src/features/cart/`, `src/features/checkout/`, `src/widgets/`

## 2. TanStack Query — Hooks por dominio

- [ ] 2.1 Crear `src/entities/producto/useProductos.ts` con useQuery para listar productos (filtros, paginación) y useQuery para detalle
- [ ] 2.2 Crear `src/entities/producto/useCategorias.ts` con useQuery para listar categorías
- [ ] 2.3 Crear `src/entities/pedido/usePedidos.ts` con useQuery para listar pedidos propios y useQuery para detalle
- [ ] 2.4 Crear `src/entities/pedido/useCrearPedido.ts` con useMutation para POST /pedidos + invalidación de queries
- [ ] 2.5 Crear `src/entities/auth/useAuth.ts` con hooks para login, register, logout, refresh (useMutation)
- [ ] 2.6 Crear `src/entities/admin/useAdmin.ts` con useQuery para stats del dashboard y useMutation para transiciones de estado
- [ ] 2.7 Migrar `HomePage.tsx` de useEffect a useProductos
- [ ] 2.8 Migrar `ProductListPage.tsx` de useEffect a useProductos con filtros
- [ ] 2.9 Migrar `ProductDetailPage.tsx` de useEffect a useProductos
- [ ] 2.10 Migrar `OrdersPage.tsx` y `OrderDetailPage.tsx` de useEffect a usePedidos
- [ ] 2.11 Migrar `AdminDashboard.tsx` de useEffect a useAdmin
- [ ] 2.12 Migrar `Admin CRUD pages` de useEffect a useProductos/useCategorias (ProductosAdminPage, CategoriasAdminPage, ClientesAdminPage, PedidosAdminPage)

## 3. Zustand — paymentStore y uiStore

- [ ] 3.1 Crear `src/stores/paymentStore.ts`: estado { status, mpPaymentId, errorDetail }, acciones { setPaymentStatus, resetPayment }
- [ ] 3.2 Crear `src/stores/uiStore.ts`: estado { theme, sidebarOpen, toasts[] }, acciones { toggleTheme, toggleSidebar, addToast, dismissToast }, persistencia selectiva del theme
- [ ] 3.3 Integrar paymentStore en `PaymentPage.tsx` (reemplazar estado local de paymentState)
- [ ] 3.4 Integrar uiStore en layouts: `Navbar.tsx` (sidebar toggle), layouts (tema oscuro/claro)

## 4. recharts — Dashboard con gráficos

- [ ] 4.1 Instalar `recharts` en frontend
- [ ] 4.2 Crear endpoint `GET /api/v1/admin/stats/detailed` que devuelva: ingresos_por_dia (últimos 7 días), pedidos_por_estado (conteo por estado), top_productos (top 5 por cantidad vendida)
- [ ] 4.3 Crear componente `IngresosChart.tsx` (gráfico de línea con recharts LineChart)
- [ ] 4.4 Crear componente `PedidosPorEstadoChart.tsx` (gráfico de torta con recharts PieChart)
- [ ] 4.5 Crear componente `TopProductosChart.tsx` (gráfico de barras con recharts BarChart)
- [ ] 4.6 Integrar charts en `AdminDashboard.tsx` manteniendo las cards de métricas existentes

## 5. Backend — HistorialEstadoPedido

- [ ] 5.1 Crear modelo `app/models/historial_estado.py`: tabla historial_estado_pedido con id, pedido_id (FK), estado_desde, estado_hasta, usuario_id (nullable), observacion, creado_en
- [ ] 5.2 Crear `app/pedidos/historial_repository.py`: métodos create(historial) y list_by_pedido(pedido_id)
- [ ] 5.3 Generar migración Alembic para la nueva tabla
- [ ] 5.4 Modificar `app/pedidos/service.py` para registrar historial en cada transición de estado
- [ ] 5.5 Incluir historial en la respuesta de GET /api/v1/pedidos/{id}
- [ ] 5.6 Modificar el seed de estado_pedido si es necesario para incluir IDs estables

## 6. Backend — Snapshot pattern

- [ ] 6.1 Agregar campo `direccion_snapshot: str | None` al modelo Pedido (JSON serializado de la dirección)
- [ ] 6.2 Modificar `app/pedidos/service.py` para capturar direccion_snapshot al crear pedido
- [ ] 6.3 Renombrar semánticamente `precio_unitario` en DetallePedido a `precio_snapshot` (o mantener como está y asegurar que se captura al crear)
- [ ] 6.4 Incluir direccion_snapshot en PedidoRead/PedidoDetail response schemas
- [ ] 6.5 Generar migración Alembic para el nuevo campo

## 7. Backend — Stock management atómico

- [ ] 7.1 Agregar método `decrement_stock(producto_id, cantidad)` a ProductoRepository usando SELECT FOR UPDATE
- [ ] 7.2 Agregar método `restore_stock(producto_id, cantidad)` a ProductoRepository
- [ ] 7.3 Modificar `app/pedidos/service.py` para llamar decrement_stock al transicionar PENDIENTE → CONFIRMADO
- [ ] 7.4 Modificar `app/pedidos/service.py` para llamar restore_stock al cancelar un pedido CONFIRMADO
- [ ] 7.5 Agregar validación: si no hay stock suficiente, la transición falla con HTTP 400

## 8. Frontend — Feature-Sliced Design (FSD)

- [ ] 8.1 Mover tipos compartidos a `src/shared/types/` (Pedido, Producto, Categoria, Pago, Direccion, Usuario)
- [ ] 8.2 Mover apiClient a `src/shared/api/apiClient.ts`
- [ ] 8.3 Mover componentes UI base a `src/shared/ui/` (Button, Input, Modal, Skeleton, EmptyState, Toast)
- [ ] 8.4 Migrar hooks existentes a entidades: `useCart.ts` → `src/features/cart/useCart.ts`, `useProducts.ts` → `src/entities/producto/useProductos.ts`, `useMercadoPago.ts` → `src/features/checkout/useMercadoPago.ts`
- [ ] 8.5 Reorganizar componentes: `ProductCard.tsx`, `ProductGrid.tsx` → `src/entities/producto/`; `Pagination.tsx` → `src/shared/ui/`; `Navbar.tsx` → `src/widgets/`
- [ ] 8.6 Reorganizar layouts: `LayoutPublic.tsx`, `LayoutAuth.tsx`, `LayoutAdmin.tsx` → `src/widgets/`
- [ ] 8.7 Reorganizar componentes admin compartidos a `src/features/admin/`
- [ ] 8.8 Mantener compatibilidad backward: los imports antiguos deben seguir funcionando o actualizar todas las referencias

## 9. Error Handling — Backend RFC 7807

- [ ] 9.1 Crear middleware/excepción handler global en FastAPI que capture HTTPException y formatee como Problem Details (RFC 7807)
- [ ] 9.2 Definir estructura estándar: { type, title, status, detail, instance, errors[] }
- [ ] 9.3 Mapear errores de validación Pydantic al formato errors[] con field + message
- [ ] 9.4 Asegurar que errores 500 no expongan stack traces en producción

## 10. Error Handling — Frontend

- [ ] 10.1 Crear `ErrorBoundary.tsx` en `src/shared/ui/` con fallback UI y botón de reload
- [ ] 10.2 Envolver layouts con ErrorBoundary
- [ ] 10.3 Crear `ToastContainer.tsx` que renderiza toasts desde uiStore
- [ ] 10.4 Agregar ToastContainer a los layouts (LayoutAuth, LayoutAdmin)
- [ ] 10.5 Actualizar llamadas API para usar toasts en lugar de estados de error locales (cuando corresponda)

## 11. Tests

- [ ] 11.1 Escribir tests unitarios para HistorialEstadoRepository
- [ ] 11.2 Escribir tests unitarios para stock decrement/restore en ProductoRepository
- [ ] 11.3 Escribir tests de integración para historial en endpoints de pedidos
- [ ] 11.4 Escribir tests de integración para stock management en flujo confirmar/cancelar pedido
- [ ] 11.5 Escribir tests para paymentStore y uiStore
- [ ] 11.6 Verificar que los tests existentes siguen pasando después de las migraciones

## 12. Verificación

- [ ] 12.1 Verificar que TanStack Query funciona: navegar catálogo, ver detalle, crear pedido — todo sin useEffects
- [ ] 12.2 Verificar paymentStore: flujo de pago completo con estados idle→processing→success/error
- [ ] 12.3 Verificar uiStore: toggle theme persiste al recargar, toasts aparecen y desaparecen
- [ ] 12.4 Verificar dashboard con recharts: gráficos cargan con datos reales
- [ ] 12.5 Verificar historial: crear pedido → confirmar → ver historial en detalle
- [ ] 12.6 Verificar snapshots: cambiar precio de producto después de crear pedido → el pedido muestra precio original
- [ ] 12.7 Verificar stock: crear pedido → confirmar → stock decrementado. Cancelar → stock restaurado
- [ ] 12.8 Verificar error handling: 404, 403, 500 muestran mensajes consistentes
- [ ] 12.9 Ejecutar `cd backend && pytest` — todos los tests pasan
- [ ] 12.10 Ejecutar `cd frontend && npx vitest run` — todos los tests pasan
