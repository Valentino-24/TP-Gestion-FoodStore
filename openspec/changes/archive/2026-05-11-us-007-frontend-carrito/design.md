## Context

FoodStore tiene frontend base (us-005) y catálogo de productos (us-006) funcionales, pero el backend de pedidos, pagos y direcciones son placeholders — no existen modelos SQLModel, routers, servicios ni repositorios. Este cambio implementa todo el flujo de compra de punta a punta.

**Backend existente**: modelos seed de `EstadoPedido` (6 estados: PENDIENTE → ENTREGADO + CANCELADO) y `FormaPago` (Tarjeta crédito/débito). Patrón feature-first con SQLModel + repository + service.

**Frontend existente**: Vite + React + TS, Zustand, axios con interceptors JWT, layouts.

## Goals / Non-Goals

**Goals:**
- Backend: modelos Pedido, PedidoItem, Pago, Direccion con SQLModel
- Backend: CRUD de pedidos con máquina de estados (FSM)
- Backend: CRUD de direcciones asociadas al usuario autenticado
- Backend: Pago con MercadoPago (SDK) + webhook
- Frontend: Carrito de compras con Zustand store persistido
- Frontend: Checkout con selección de dirección + pago
- Frontend: Historial de pedidos + detalle
- Frontend: CRUD de direcciones desde el perfil

**Non-Goals:**
- Panel admin de pedidos (us-008)
- Notificaciones email/ws
- Cupones de descuento
- Wishlist / lista de deseos

## Decisions

### 1. Máquina de estados en Pedido (FSM)
**Decisión**: Validar transiciones de estado en el service con un mapa de transiciones válidas. Cada estado sabe a qué estados puede transicionar.

**Estados**: PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO. CANCELADO accesible desde PENDIENTE y CONFIRMADO.

### 2. Carrito con Zustand store (frontend)
**Decisión**: Store de carrito con Zustand + persistencia en localStorage. Acciones: addItem, removeItem, updateQuantity, clearCart.

**Alternativa**: Carrito en backend (session/cache) — descartado porque es más complejo y el carrito no necesita persistencia server-side.

### 3. Pedido se crea en checkout
**Decisión**: El carrito es local. Al hacer checkout se envía `POST /pedidos` con items, dirección_id y forma_pago_id. El backend crea el Pedido + PedidoItems y devuelve el ID para proceder al pago.

### 4. Integración MercadoPago
**Decisión**: Usar SDK oficial `mercadopago` (Python). `POST /pagos` recibe `pedido_id` y `mp_token` (token de tarjeta desde frontend). El webhook `POST /webhooks/mercadopago` actualiza el estado del pedido.

**Alternativa**: Pago simulado (sin MP) — podría agregarse como fallback si no hay credenciales de MP configuradas.

### 5. Direcciones asociadas al usuario
**Decisión**: `Direccion.user_id` FK al usuario autenticado. El CRUD filtra por `user_id` automáticamente (cada usuario ve solo sus direcciones).

## Risks / Trade-offs

- **[MercadoPago requiere credenciales]** → Sin `MP_ACCESS_TOKEN` configurado, los pagos fallan. Agregar endpoint de pago simulado como fallback para desarrollo.
- **[Carrito local se pierde al cerrar pestaña sin checkout]** → Persistencia en localStorage mitiga esto. No hay carrito跨-sesión (no es necesario para el alcance actual).
- **[Transiciones de estado concurrentes]** → El service valida el estado actual antes de cada transición. Usar bloqueo optimista si hay contención.
- **[Seed data de formas de pago limitada]** → Solo 2 formas de pago semilla. MP token replacement permite cualquier tarjeta.
