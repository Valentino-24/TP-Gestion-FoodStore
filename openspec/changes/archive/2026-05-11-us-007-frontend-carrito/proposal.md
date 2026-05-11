## Why

El catálogo de productos ya funciona, pero los usuarios no pueden comprar nada. No existe carrito, checkout, ni gestión de pedidos. El backend tiene los módulos de pedidos, pagos y direcciones como placeholders — sin modelos, sin APIs. Este cambio implementa todo el flujo de compra completo: desde agregar al carrito hasta pagar y ver el historial de pedidos.

## What Changes

**Backend:**
- Crear modelos `Pedido` (con FSM de estados), `PedidoItem`, `Pago`, `Direccion`
- Implementar CRUD de pedidos con máquina de estados (PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO, o CANCELADO desde cualquier estado activo)
- Implementar CRUD de direcciones asociadas al usuario autenticado
- Implementar pago con MercadoPago (POST /pagos, webhook de confirmación)
- Registrar los routers en `main.py`

**Frontend:**
- Crear carrito de compras local (Zustand store, persistido en localStorage)
- Página `/carrito` con items, cantidades, subtotal y botón "Ir al checkout"
- Página `/checkout` con selección de dirección + forma de pago + resumen
- Página `/pedidos` con historial de pedidos del usuario
- Página `/pedidos/:id` con detalle del pedido y estado actual
- Página `/perfil/direcciones` para gestionar direcciones de envío

## Capabilities

### New Capabilities
- `pedidos-api`: Backend de pedidos con modelo, FSM, CRUD y endpoints REST
- `pagos-api`: Backend de pagos con integración MercadoPago
- `direcciones-api`: Backend de direcciones con CRUD asociado al usuario
- `shopping-cart`: Carrito de compras frontend con Zustand store y persistencia
- `checkout-flow`: Flujo de checkout frontend (dirección → pago → confirmación)
- `orders-history`: Historial y detalle de pedidos frontend

### Modified Capabilities
- `frontend-base`: Se agregan las rutas `/carrito`, `/checkout`, `/pedidos`, `/pedidos/:id`, `/perfil/direcciones`

## Impact

- **Backend**: 3 nuevos módulos (pedidos/, pagos/, direcciones/) con modelos SQLModel, schemas Pydantic, repositorios, servicios y routers
- **Frontend**: Nuevas páginas y store de carrito, conexión con nuevas APIs
- **main.py**: Registrar 3 nuevos routers
- **Dependencias**: SDK de MercadoPago (`mercadopago`) en backend
- **Base de datos**: Nuevas tablas (pedido, pedido_item, pago, direccion)
