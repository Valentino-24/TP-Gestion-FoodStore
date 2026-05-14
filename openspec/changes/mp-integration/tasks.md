## 1. Configuración de credenciales MP

- [x] 1.1 Actualizar `backend/.env` con `MP_ACCESS_TOKEN` y `MP_PUBLIC_KEY` reales (test)
- [x] 1.2 Agregar `VITE_MP_PUBLIC_KEY` en `frontend/.env`
- [x] 1.3 Agregar "Efectivo" (id=3) como forma_pago en `backend/seed_db.py`
- [x] 1.4 Agregar "Efectivo" (id=3) como forma_pago en `backend/app/db/seed.py`

## 2. Backend — Fix condición de MercadoPago SDK

- [x] 2.1 Modificar `app/pagos/service.py` para usar MP SDK cuando `MP_ACCESS_TOKEN` esté configurado (sin importar si es `TEST-` o `APP_USR-`)
- [x] 2.2 Cambiar el metodo del Pago de "simulado" a "mercadopago" cuando se usa el SDK
- [x] 2.3 Retornar HTTP 503 si no hay token configurado (en lugar de simular)

## 3. Backend — Manejo de Efectivo

- [x] 3.1 Ajustar `app/pagos/service.py` para que no cree Pago si la forma_pago es Efectivo
- [x] 3.2 Verificar que el pedido con Efectivo queda en PENDIENTE y no requiere pago

## 4. Frontend — Instalación y configuración de MercadoPago.js

- [x] 4.1 Cargar MercadoPago SDK v3 (script directo desde CDN, sin npm package)
- [x] 4.2 Crear hook/utilitario `useMercadoPago` que inicialice el SDK con la public key y maneje la carga del script

## 5. Frontend — PaymentPage con Card Payment Brick

- [x] 5.1 Reemplazar el botón "Pagar ahora" simulado por el Card Payment Brick de MercadoPago
- [x] 5.2 Manejar evento `onSubmit` del brick: generar token y enviarlo a `POST /api/v1/pagos`
- [x] 5.3 Mostrar estado de procesamiento mientras se crea el pago
- [x] 5.4 Mostrar pantalla de éxito con enlace al pedido cuando el pago se aprueba
- [x] 5.5 Mostrar error con opción de reintentar cuando el pago es rechazado

## 6. Frontend — CheckoutPage con Efectivo

- [x] 6.1 Agregar "Efectivo" como opción de forma de pago en el listado hardcodeado
- [x] 6.2 Redirigir a `/pedidos` si el usuario eligió Efectivo (en lugar de `/pago/{id}`)
- [x] 6.3 Mantener redirección a `/pago/{id}` si el usuario eligió tarjeta

## 7. Verificación

- [ ] 7.1 Verificar que el Card Payment Brick se renderiza correctamente en la página de pago
- [ ] 7.2 Verificar que al pagar con tarjeta de prueba el pago se aprueba y el pedido pasa a CONFIRMADO
- [ ] 7.3 Verificar que al elegir Efectivo el pedido se crea sin redirigir a pago
- [ ] 7.4 Verificar que el admin puede confirmar un pedido en efectivo desde el panel
