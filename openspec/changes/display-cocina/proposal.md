## Why

Food Store no tiene un display de cocina (KDS) ni un rol dedicado para el equipo de cocina. Hoy la operación de preparación de pedidos está absorbida completamente por el rol `PEDIDOS`/`ADMIN`, sin una pantalla dedicada que muestre en tiempo real qué pedidos hay que preparar, cuáles están en preparación y hace cuánto esperan. Esto obliga al cocinero a recargar manualmente la lista de pedidos o a coordinarse por fuera del sistema.

Se necesita un **Kitchen Display System (KDS)** adaptado al modelo de delivery: una pantalla de cocina en tiempo real con un rol `COCINA` que solo vea los pedidos que debe preparar y pueda avanzar el FSM dentro de la fase de cocina (`CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO`).

## What Changes

- **Nuevo rol `COCINA`**: registro en tabla catálogo `Rol`, seed idempotente, relacional N:M con `UsuarioRol`.
- **KDS Backend (SSE)**: endpoint `GET /api/v1/cocina/pedidos` (carga inicial + fallback polling) y endpoint `GET /api/v1/cocina/eventos` (SSE stream para tiempo real).
- **Sistema de eventos en proceso**: pub/sub con `asyncio` para emitir eventos cuando un pedido cambia de estado en la fase de cocina.
- **Eventos emitidos**: `PEDIDO_CONFIRMADO` (aparece en KDS), `PEDIDO_EN_PREPARACION` (se mueve de columna), `PEDIDO_EN_CAMINO` / `PEDIDO_CANCELADO` (desaparece del KDS).
- **Validación de transiciones por rol**: el servicio del FSM valida qué transiciones puede ejecutar cada rol (el cocinero solo `CONFIRMADO → EN_PREP` y `EN_PREP → EN_CAMINO`).
- **Pantalla KDS frontend**: ruta `/cocina` con layout de dos columnas ("Por preparar" / "En preparación"), tarjetas con items, exclusiones, notas y timer de urgencia.
- **Indicador de urgencia**: timer visual por tiempo en cola de cocina (<10min normal, 10-20 naranja, >20 rojo), calculado en cliente cada 15s.
- **Resiliencia**: fallback por polling cada 30s si SSE se desconecta, reconexión automática.
- **Alerta opcional (US-COCINA-05)**: notificación sonora + flash visual al llegar pedido nuevo.

**No se modifican** estados del FSM ni se agregan tablas nuevas en la v1.

## Capabilities

### New Capabilities
- `kds-backend`: Backend del Kitchen Display System — endpoints REST + SSE, sistema de eventos pub/sub en proceso para tiempo real, autorización por transición para el rol COCINA.
- `kds-frontend`: Pantalla de cocina en React — ruta `/cocina`, layout de columnas, tarjetas con timer de urgencia, conexión SSE con fallback polling, alerta auditiva/visual.

### Modified Capabilities
- `pedidos-api`: Se modifica la autorización del endpoint `PATCH /pedidos/{id}/estado` para admitir el rol `COCINA`, y la validación en el servicio del FSM ahora verifica **qué transición** permite cada rol (no solo quién accede al endpoint).
- `rbac`: Se agrega el rol `COCINA` al catálogo de roles. Se actualiza la tabla de autorización de transiciones.

## Impact

- **Backend**: Nuevo módulo `backend/app/cocina/` con router SSE + REST, gestor de conexiones SSE, publicación de eventos en `PedidoService`. Modificación del `PedidoService.update_estado()` para validar por rol. Agregar `COCINA` al seed de roles.
- **Frontend**: Nueva ruta `/cocina` con layout protegido por rol (`COCINA`/`PEDIDOS`/`ADMIN`). Nuevos componentes: `KDSPage`, `OrdenCard`, `TimerUrgencia`. Hook `useCocinaSSE` para conexión SSE con fallback polling. Store de cocina en Zustand (pedidos visibles, tiempos).
- **Dependencias**: Ninguna nueva. SSE usa `EventSource` nativo del browser y `StreamingResponse` de FastAPI. Sin Redis, sin WebSocket, sin librerías externas.
- **Infra**: Pub/sub en proceso (`asyncio`). Límite conocido: en múltiples instancias del backend se necesitaría Redis Pub/Sub para que los eventos lleguen a todas las instancias.
