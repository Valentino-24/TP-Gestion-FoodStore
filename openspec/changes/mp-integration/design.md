## Context

Actualmente el pago es simulado: `PaymentPage.tsx` tiene un botón "Pagar ahora" que llama a `POST /pagos/` y el backend aprueba automáticamente sin importar qué. El SDK de MercadoPago (`mercadopago` 2.4.0) ya está instalado en el backend, pero la condición `if token and not token.startswith("TEST-")` lo saltea incluso cuando hay credenciales de prueba configuradas.

En el frontend no hay ningún paquete de MercadoPago instalado. El `CheckoutPage.tsx` tiene hardcodeadas dos formas de pago: "Tarjeta de crédito" y "Tarjeta de débito", y siempre redirige a `/pago/{id}`.

Las credenciales de prueba de MP ya fueron provistas por el usuario.

## Goals / Non-Goals

**Goals:**
- Reemplazar el pago simulado por integración real con MercadoPago usando Card Payment Brick
- Agregar "Efectivo" como método de pago que no requiere paso por PaymentPage
- El admin confirma manualmente los pedidos en efectivo desde el panel de administración
- Funcionar correctamente tanto con tokens de prueba (`TEST-`) como productivos (`APP_USR-`)

**Non-Goals:**
- No se implementan otros Bricks de MP (Wallet, Pix, etc.) — solo tarjeta
- No se implementan pagos recurrentes / suscripciones
- No se implementa la cuenta regresiva de expiración de pago
- No se cambia el modelo de datos de Pago ni de Pedido (solo seed de forma_pago)

## Decisions

### 1. Card Payment Brick (vs. construir el form manualmente)
**Decisión**: Usar el Card Payment Brick de MercadoPago.
**Razón**: Es PCI DSS compliant, MercadoPago maneja los datos sensibles de la tarjeta, no pasa la data por nuestro servidor. Genera un token que usamos para crear el pago. El SDK (`@mercadopago/sdk-js`) proporciona el brick como un web component, se monta en un `<div>` y emite eventos cuando se genera el token.
**Alternativa**: Construir el form a mano y usar `MercadoPago.createCardToken()`. Descartado porque requiere certificación PCI DSS.

### 2. Token MP se envía al backend en el payload de creación de pago
**Decisión**: El Card Brick genera un `token` que se envía en el body de `POST /pagos/` como `mp_token`.
**Razón**: El backend ya tiene el campo `mp_token: Optional[str]` en `PagoCreate`. Solo hay que pasarlo al SDK de MP al crear el payment.

### 3. Efectivo no crea registro de Pago
**Decisión**: Si la `forma_pago_id` corresponde a Efectivo, el pedido se crea sin generar un Pago. El admin cambia el estado manualmente de PENDIENTE a CONFIRMADO cuando cobra.
**Razón**: No hay transacción financiera que registrar contra MP. El FSM ya soporta `PENDIENTE → CONFIRMADO`.

### 4. Condición de uso del SDK de MP
**Decisión**: Cambiar de `if token and not token.startswith("TEST-")` (solo productivo) a `if token` (cualquier token no vacío).
**Razón**: Los tokens de prueba son válidos para hacer llamadas al SDK de MP. La condición anterior los ignoraba deliberadamente, lo que obligaba a hacer simulación incluso teniendo credenciales.

### 5. Redirección condicional post-pedido
**Decisión**: El frontend decide a dónde redirigir según la forma de pago seleccionada en el checkout.
**Razón**: Es más simple que hacer que el backend retorne un "tipo de pago" y evita una llamada extra.

## Risks / Trade-offs

- **[Token expirado]**: El token de tarjeta generado por MercadoPago expira. Si el usuario tarda mucho en llenar el formulario, puede vencer. → Mitigación: MP Brick maneja esto internamente y regenera el token si es necesario.
- **[Webhooks en localhost]**: MercadoPago no puede enviar webhooks a localhost. → Mitigación: usamos ngrok para pruebas locales, o simplemente verificamos el payment de forma sincrónica (el SDK ya retorna el status en la creación).
- **[UX del Brick]**: El Card Payment Brick tiene un estilo definido por MP que puede no coincidir exactamente con el diseño actual. → Mitigación: el brick soporta personalización básica de colores y fuentes. Aceptamos pequeñas diferencias visuales.
- **[Sin pago recurrente]**: Si en el futuro se necesita guardar tarjetas para compras futuras, habrá que migrar a Customer Cards. → No es blocking ahora, se puede agregar después.
