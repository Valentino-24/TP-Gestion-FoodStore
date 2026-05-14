## Why

El flujo de pago actual es completamente simulado: no hay forma de ingresar datos de tarjeta reales y el backend aprueba automáticamente sin integrar MercadoPago. Además, no existe la opción de pago en efectivo para entregas contra pago. Esto bloquea el uso real del sistema en producción.

## What Changes

- **Pago con tarjeta real**: Reemplazar el botón "Pagar ahora" simulado por un formulario de tarjeta (número, vencimiento, CVV, titular) usando MercadoPago Card Payment Brick, que genera un token seguro que se envía al backend para crear el pago real.
- **Opción Efectivo**: Agregar "Efectivo" como método de pago. Al seleccionarlo, el pedido se crea sin requerir paso por la página de pago. El admin confirma manualmente el pedido cuando recibe el pago.
- **Credenciales MP**: Configurar `MP_ACCESS_TOKEN` y `MP_PUBLIC_KEY` de prueba en el entorno. El backend ahora usa MercadoPago SDK tanto con tokens `TEST-` como `APP_USR-` (antes ignoraba los de prueba).
- **Comportamiento diferencial en Checkout**: Si el usuario elige Efectivo, después de crear el pedido se redirige a `/pedidos` (sin pago). Si elige tarjeta, se redirige a `/pago/{id}` con el formulario de MercadoPago.

## Capabilities

### New Capabilities
- `card-payment-ui`: Componente frontend de formulario de pago con tarjeta usando MercadoPago Card Payment Brick. Incluye la inicialización del SDK de MercadoPago, el renderizado del brick, y la obtención del token de tarjeta.

### Modified Capabilities
- `pagos-api`: Cambiar la lógica de creación de pagos para que use MercadoPago SDK cuando hay token configurado (sin importar si es `TEST-` o `APP_USR-`). Agregar soporte para el método "Efectivo" donde el pedido no requiere pago previo.
- `checkout-flow`: Agregar "Efectivo" como opción de forma de pago. Modificar el flujo post-creación de pedido para redirigir a pedidos si es efectivo, o a la página de pago con tarjeta si es tarjeta. La página de pago ahora muestra el Card Payment Brick en lugar de un botón simulado.

## Impact

- **Backend**: `app/pagos/service.py` — cambiar condición de uso de MP SDK. `app/pagos/schemas.py` — posible ajuste en `PagoCreate` para recibir `mp_token`. `app/pagos/router.py` — sin cambios mayores. `seed_db.py` — agregar `Efectivo` en `forma_pago`.
- **Frontend**: `src/pages/PaymentPage.tsx` — reemplazar botón simulado por Card Payment Brick. `src/pages/CheckoutPage.tsx` — agregar opción Efectivo, redirigir condicionalmente. Agregar `VITE_MP_PUBLIC_KEY` a `.env`. Instalar `@mercadopago/sdk-js`.
- **Dependencias**: `@mercadopago/sdk-js` (npm), `mercadopago` ya instalado (backend).
- **Config**: Actualizar `backend/.env` con `MP_ACCESS_TOKEN` real. Agregar `VITE_MP_PUBLIC_KEY` en `frontend/.env`.
