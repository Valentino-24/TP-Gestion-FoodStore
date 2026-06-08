## Context

Food Store hoy es una API REST pura (FastAPI + PostgreSQL + React). No tiene infraestructura de tiempo real, no tiene WebSockets ni Redis. Los pedidos ya tienen un FSM implementado con 6 estados (`PENDIENTE`, `CONFIRMADO`, `EN_PREPARACION`, `EN_CAMINO`, `ENTREGADO`, `CANCELADO`) y el endpoint `PATCH /pedidos/{id}/estado` solo permite transiciones a ADMIN.

El RBAC tiene 4 roles: `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`. No existe un rol `COCINA`.

El `HistorialEstadoPedido` ya está implementado (modelo, repositorio, migración, registro en cada transición). El pago aprobado dispara automáticamente `PENDIENTE → CONFIRMADO`.

## Goals / Non-Goals

**Goals:**
- Agregar el rol `COCINA` al catálogo de roles con seed idempotente.
- Crear un endpoint REST `GET /api/v1/cocina/pedidos` que devuelva pedidos en `CONFIRMADO` y `EN_PREP` ordenados por antigüedad.
- Crear un endpoint SSE `GET /api/v1/cocina/eventos` que emita eventos en tiempo real cuando cambien pedidos en fase de cocina.
- Modificar `PATCH /pedidos/{id}/estado` para que `COCINA` pueda ejecutar solo `CONFIRMADO → EN_PREP` y `EN_PREP → EN_CAMINO`.
- Implementar pantalla KDS en React con columnas "Por preparar" / "En preparación", tarjetas y timer de urgencia.
- Proveer resiliencia: fallback por polling si SSE se desconecta.

**Non-Goals:**
- No se agregan estados nuevos al FSM (no hay `LISTO` intermedio).
- No se agregan tablas nuevas a la BD en v1.
- No se implementa multi-instancia ni Redis Pub/Sub (queda como límite conocido).
- `COCINA` no cancela pedidos, no despacha (`EN_CAMINO → ENTREGADO`), no tiene CRUD.
- `US-COCINA-07` (marcar producto no disponible) queda fuera de v1 por solapamiento con rol `STOCK`.

## Decisions

### D-1: SSE sobre WebSocket para tiempo real

**Decisión:** Usar Server-Sent Events (SSE) en lugar de WebSocket.

**Razonamiento:** El KDS es un flujo **unidireccional**: el servidor envía eventos al cliente (pedido nuevo, cambio de estado, etc.). El cocinero no necesita enviar datos por el canal de tiempo real — las acciones (tomar pedido, marcar terminado) se hacen vía REST. SSE:
- Se implementa con `StreamingResponse` de FastAPI + `EventSource` nativo del browser — cero dependencias nuevas.
- Reconexión automática nativa en el browser.
- Más simple de testear (se puede probar con `TestClient` de FastAPI en modo streaming).
- WebSocket sería justificable si el cocinero necesitara enviar datos frecuentes por el canal, pero no es el caso.

**Alternativa considerada:** WebSocket — bidireccional, más complejo, requiere `websockets` o el `WebSocket` nativo de FastAPI. No agrega valor para este caso de uso.

### D-2: Pub/Sub en proceso con asyncio

**Decisión:** Usar un `EventManager` con un `set[asyncio.Queue]` para broadcast de eventos en single-instancia.

**Razonamiento:** En una instancia single-process de FastAPI (con `uvicorn`), todas las conexiones SSE viven en el mismo proceso. Un manager con colas asyncio alcanza perfectamente para broadcast:
```python
class EventManager:
    def __init__(self):
        self._queues: set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue):
        self._queues.discard(queue)

    async def broadcast(self, event: dict):
        dead = set()
        for q in self._queues:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                dead.add(q)
        self._queues -= dead
```

**Alternativa considerada:** Redis Pub/Sub — necesaria para multi-instancia pero overkill para v1. Se documenta como límite conocido en `design.md`.

### D-3: Eventos emitidos desde PedidoService

**Decisión:** El `PedidoService` (existente) recibe una dependencia del `EventManager` y emite eventos después de cada transición de estado relevante.

**Razonamiento:** Ya existe un único punto de control para los cambios de estado (`PedidoService.update_estado()` y `PagoService`). Emitir eventos desde ahí garantiza que no haya caminos que omitan la notificación. Alternativa (eventos desde el repositorio) sería más frágil y menos explícita.

### D-4: Validación de transiciones por rol en el servicio del FSM

**Decisión:** Agregar un mapa `ROLE_TRANSITIONS` en `PedidoService` que defina qué roles pueden ejecutar qué transiciones. Esto es independiente del `require_role` del endpoint.

**Razonamiento:** El `require_role(["COCINA", "PEDIDOS", "ADMIN"])` en el endpoint permite el acceso al endpoint, pero NO valida qué transición específica se pide. Un cocinero podría pedir `EN_PREP → ENTREGADO` y pasar el `require_role`. La validación fina se hace en el servicio, contra un mapa como:
```python
ROLE_TRANSITIONS = {
    "COCINA": {("CONFIRMADO", "EN_PREP"), ("EN_PREP", "EN_CAMINO")},
    "PEDIDOS": {("CONFIRMADO", "EN_PREP"), ("EN_PREP", "EN_CAMINO"), ("EN_CAMINO", "ENTREGADO"), ...},
    "ADMIN": ...,  # todas
}
```

### D-5: Timer de urgencia 100% en el cliente

**Decisión:** El frontend calcula el timer a partir del timestamp de entrada a cocina que envía el backend.

**Razonamiento:** Simplifica el backend (no necesita cron jobs ni timers). El timestamp se obtiene del `HistorialEstadoPedido.created_at` del registro donde `estado_hasta = CONFIRMADO`. El frontend recalcula cada 15s con `setInterval`.

## Risks / Trade-offs

- **[Alta] Single-instancia limitada:** El pub/sub en proceso solo funciona con una instancia del backend. Si se escala a múltiples workers/instancias, los eventos no llegarán a todas las conexiones. **Mitigación:** Documentado como límite conocido. Migrar a Redis Pub/Sub si se necesita multi-instancia.
- **[Media] Pérdida de eventos sin conexión:** Si un cocinero se desconecta y reconecta, los eventos ocurridos durante la desconexión se pierden (la v1 no persiste eventos). **Mitigación:** Al reconectar SSE, el frontend hace un fetch completo de `GET /cocina/pedidos` para refrescar el estado actual.
- **[Media] Autoplay policy del browser:** La alerta sonora (US-COCINA-05) requiere una interacción previa del usuario con la página. **Mitigación:** El sonido solo se reproduce después del primer click/tap del usuario en la página. Se muestra un indicador si el audio está bloqueado.
- **[Baja] Polling y SSE simultáneos:** Durante reconexión, tanto SSE como polling pueden estar activos brevemente, causando duplicados. **Mitigación:** El estado se maneja por ID de pedido; duplicados se ignoran en el frontend.
