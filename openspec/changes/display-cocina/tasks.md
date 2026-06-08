## 1. Backend — Rol COCINA y seed

- [x] 1.1 Agregar `COCINA` (codigo='COCINA', nombre='Cocinero') al seed de roles en `backend/app/db/seed.py` con `INSERT ... ON CONFLICT DO NOTHING`
- [x] 1.2 Agregar `COCINA` al seed de roles en `backend/seed_db.py` (mismo patrón)
- [x] 1.3 Crear usuario de prueba `cocina@foodstore.com` con rol COCINA en ambos seeds

## 2. Backend — EventManager (pub/sub en proceso)

- [x] 2.1 Crear `backend/app/cocina/event_manager.py` con clase `EventManager`: un `dict[str, set[asyncio.Queue]]` de canales de eventos
- [x] 2.2 Implementar `subscribe(channel) -> asyncio.Queue`: crea una cola y la registra en el canal
- [x] 2.3 Implementar `unsubscribe(channel, queue)`: remueve la cola del canal
- [x] 2.4 Implementar `broadcast(channel, event)`: pone el evento en todas las colas del canal (non-blocking, descarta colas llenas)
- [x] 2.5 Exportar una instancia singleton `event_manager = EventManager()` para usar como dependencia

## 3. Backend — Módulo cocina (REST + SSE)

- [x] 3.1 Crear `backend/app/cocina/__init__.py` (puede estar vacío)
- [x] 3.2 Crear `backend/app/cocina/service.py` con `CocinaService.get_pedidos_cocina(db)`: query de pedidos en CONFIRMADO + EN_PREP, ordenados por entrada a cocina ascendente, incluyendo items y timestamp de entrada
- [x] 3.3 Crear `backend/app/cocina/schemas.py` con `CocinaPedidoResponse` y `SSEEvent` schemas
- [x] 3.4 Crear `backend/app/cocina/router.py`:
  - `GET /api/v1/cocina/pedidos` (REST, protegido con `require_role(["COCINA", "PEDIDOS", "ADMIN"])`)
  - `GET /api/v1/cocina/eventos` (SSE con `StreamingResponse`, auth por JWT vía query param o cookie)
- [x] 3.5 Implementar generación de eventos SSE en el router: formato `event: <nombre>\ndata: <json>\n\n`
- [x] 3.6 Registrar el router de cocina en `backend/app/main.py` con prefijo `/api/v1`

## 4. Backend — Validación de transiciones por rol en PedidoService

- [x] 4.1 Definir mapa `ROLE_TRANSITIONS` en `backend/app/pedidos/service.py`
- [x] 4.2 Modificar `PedidoService.update_estado()`: recibir `usuario` (User con roles) en lugar de `admin_id`, validar por rol
- [x] 4.3 Loguear el `usuario_id` correcto en `HistorialEstadoPedido` según quién ejecutó la transición
- [x] 4.4 Modificar el router `PATCH /api/v1/pedidos/{id}/estado`: `require_role(["COCINA", "PEDIDOS", "ADMIN"])`, pasar usuario completo

## 5. Backend — Emisión de eventos desde PedidoService

- [x] 5.1 Inyectar `EventManager` en `PedidoService` (parámetro opcional en `__init__`)
- [x] 5.2 Emitir evento `PEDIDO_CONFIRMADO` cuando el pago aprueba la transición PENDIENTE → CONFIRMADO (en `PagoService` también)
- [x] 5.3 Emitir `PEDIDO_EN_PREPARACION` en CONFIRMADO → EN_PREP
- [x] 5.4 Emitir `PEDIDO_EN_CAMINO` en EN_PREP → EN_CAMINO
- [x] 5.5 Emitir `PEDIDO_CANCELADO` en cualquier → CANCELADO desde CONFIRMADO o EN_PREP

## 6. Frontend — KDS store y hook SSE

- [x] 6.1 Crear `frontend/src/features/cocina/cocinaStore.ts` (Zustand): estado + acciones para manejo de pedidos KDS
- [x] 6.2 Crear `frontend/src/features/cocina/useCocinaSSE.ts`: hook SSE con reconexión y fallback polling
- [x] 6.3 Crear tipos `CocinaPedido` e `ItemPedido` en `frontend/src/features/cocina/types.ts`

## 7. Frontend — Componentes KDS

- [x] 7.1 Crear `TimerUrgencia.tsx`: timer que se actualiza cada 15s con colores por umbral
- [x] 7.2 Crear `OrdenCard.tsx`: tarjeta con items, timer, botones Iniciar preparación / Listo
- [x] 7.3 Crear `KDSPage.tsx`: layout de dos columnas con carga inicial, SSE, estados vacío/error
- [x] 7.4 Crear `KDSLayout.tsx`: layout full-screen con indicador SSE y toggle de sonido

## 8. Frontend — Routing y guards

- [x] 8.1 Crear `CocinaRoute.tsx`: guard para roles COCINA/PEDIDOS/ADMIN
- [x] 8.2 Agregar ruta `/cocina` en `router.tsx` con `CocinaRoute` y `KDSLayout`
- [x] 8.3 Agregar enlace a `/cocina` en `Navbar.tsx` para roles autorizados
- [x] 8.4 Excluir `/cocina` del auto-logout (no hay auto-logout en el proyecto; KDSLayout mantiene sesión activa)

## 9. Frontend — Alerta sonora (US-COCINA-05)

- [x] 9.1 Implementar alerta sonora con Web Audio API en `useCocinaSSE.ts` al recibir `PEDIDO_CONFIRMADO`
- [x] 9.2 Agregar toggle de sonido ON/OFF persistido en localStorage (en `KDSLayout.tsx`)

## 10. Backend — Tests

- [ ] 10.1 Test unitario de `EventManager`: subscribe, unsubscribe, broadcast, descarte de colas llenas
- [ ] 10.2 Test de integración: `GET /api/v1/cocina/pedidos` retorna solo CONFIRMADO y EN_PREP
- [ ] 10.3 Test de integración: SSE endpoint rechaza sin auth (401)
- [ ] 10.4 Test de integración: COCINA puede transicionar CONFIRMADO → EN_PREP
- [ ] 10.5 Test de integración: COCINA NO puede transicionar EN_CAMINO → ENTREGADO (403)
- [ ] 10.6 Test de integración: evento SSE se emite cuando un pedido pasa a CONFIRMADO
