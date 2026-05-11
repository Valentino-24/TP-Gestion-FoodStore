## 1. Modelos backend

- [x] 1.1 Crear `backend/app/models/pedido.py` — modelo Pedido con FSM de estados
- [x] 1.2 Crear `backend/app/models/pedido_item.py` — modelo PedidoItem con FK a Pedido y Producto
- [x] 1.3 Crear `backend/app/models/pago.py` — modelo Pago con FK a Pedido
- [x] 1.4 Crear `backend/app/models/direccion.py` — modelo Direccion con FK a Usuario
- [x] 1.5 Actualizar `backend/app/models/__init__.py` — importar nuevos modelos

## 2. Backend: Direcciones API

- [x] 2.1 Crear `backend/app/direcciones/schemas.py` — schemas DireccionCreate, DireccionResponse, DireccionUpdate
- [x] 2.2 Crear `backend/app/direcciones/repository.py` — repositorio CRUD con filtro por usuario
- [x] 2.3 Crear `backend/app/direcciones/service.py` — servicio con lógica de pertenencia
- [x] 2.4 Crear `backend/app/direcciones/router.py` — endpoints CRUD protegidos
- [x] 2.5 Registrar router de direcciones en `main.py`

## 3. Backend: Pedidos API

- [x] 3.1 Crear `backend/app/pedidos/schemas.py` — schemas PedidoCreate, PedidoResponse, PedidoItemSchema, EstadoUpdate
- [x] 3.2 Crear `backend/app/pedidos/repository.py` — repositorio con filtro por usuario/admin, paginación
- [x] 3.3 Crear `backend/app/pedidos/service.py` — servicio con FSM y lógica de creación (calcular total desde items)
- [x] 3.4 Crear `backend/app/pedidos/router.py` — endpoints: POST /pedidos, GET /pedidos, GET /pedidos/{id}, PATCH /pedidos/{id}/estado (admin)
- [x] 3.5 Registrar router de pedidos en `main.py`

## 4. Backend: Pagos API

- [x] 4.1 Instalar SDK MercadoPago: `pip install mercadopago`
- [x] 4.2 Crear `backend/app/pagos/schemas.py` — schemas PagoCreate, PagoResponse
- [x] 4.3 Crear `backend/app/pagos/repository.py` — repositorio de pagos
- [x] 4.4 Crear `backend/app/pagos/service.py` — servicio con integración MP (o modo simulado sin credenciales)
- [x] 4.5 Crear `backend/app/pagos/router.py` — endpoints: POST /pagos, POST /webhooks/mercadopago
- [x] 4.6 Registrar router de pagos en `main.py`

## 5. Frontend: Cart store

- [x] 5.1 Crear `frontend/src/stores/cartStore.ts` — Zustand store con addItem, removeItem, updateQuantity, clearCart, persistencia localStorage
- [x] 5.2 Crear hook `useCart` con total items, subtotal, y acciones

## 6. Frontend: Carrito page

- [x] 6.1 Crear `frontend/src/pages/CartPage.tsx` — lista de items con cantidad, precio, total, botón checkout
- [x] 6.2 Agregar badge de contador en Navbar (cantidad de items en carrito)

## 7. Frontend: Checkout flow

- [x] 7.1 Crear `frontend/src/pages/CheckoutPage.tsx` — selección de dirección + forma de pago + resumen + botón "Realizar pedido"
- [x] 7.2 Crear componente `AddressForm.tsx` — formulario de dirección (inline/modal)
- [x] 7.3 Crear `frontend/src/pages/PaymentPage.tsx` — página de pago post-checkout
- [x] 7.4 Conectar checkout con POST /api/v1/pedidos

## 8. Frontend: Orders pages

- [x] 8.1 Crear `frontend/src/pages/OrdersPage.tsx` — historial de pedidos del usuario
- [x] 8.2 Crear `frontend/src/pages/OrderDetailPage.tsx` — detalle del pedido con items, estado, pago, dirección

## 9. Frontend: Address management

- [x] 9.1 Crear `frontend/src/pages/AddressesPage.tsx` — lista de direcciones con CRUD
- [x] 9.2 Conectar con GET/POST/PUT/DELETE /api/v1/direcciones

## 10. Routing

- [x] 10.1 Actualizar `frontend/src/router.tsx` — agregar /carrito, /checkout, /pago, /pedidos, /pedidos/:id, /perfil/direcciones
- [x] 10.2 Actualizar Navbar con link a /carrito y /pedidos

## 11. Verificación final

- [x] 11.1 Verificar que `npm run build` compila sin errores (frontend) — 123 modules, 0 errors
- [x] 11.2 Verificar que el backend arranca sin errores — 37 routes OK
- [x] 11.3 Verificar CRUD de direcciones via API — POST/GET/PUT/DELETE funcionan
- [x] 11.4 Verificar creación de pedido via API — POST /pedidos OK, FSM transitions OK
- [x] 11.5 Verificar flujo completo: catálogo → carrito → checkout → pedido — Pago simulado OK, pedido → CONFIRMADO
