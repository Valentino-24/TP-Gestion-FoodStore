## 1. Backend: Admin stats endpoint

- [x] 1.1 Crear `backend/app/admin/__init__.py` y `backend/app/admin/router.py` con endpoint `GET /admin/stats` que devuelva: today_pedidos_count, today_ingresos, total_productos_activos, total_clientes_activos
- [x] 1.2 Registrar router `admin_router` en `backend/app/main.py`

## 2. Frontend: Admin Dashboard

- [x] 2.1 Reemplazar `frontend/src/pages/AdminDashboard.tsx` con cards de estadísticas (Pedidos hoy, Ingresos hoy, Productos activos, Clientes activos) con loading skeleton y error handling
- [x] 2.2 Conectar dashboard con GET /api/v1/admin/stats

## 3. Frontend: Admin Productos

- [x] 3.1 Crear `frontend/src/pages/admin/ProductosAdminPage.tsx` — tabla paginada con columnas: nombre, precio, categoría, activo, acciones
- [x] 3.2 Agregar modal/ form para crear y editar producto
- [x] 3.3 Conectar con POST/PUT/DELETE /api/v1/productos/ y refrescar tabla

## 4. Frontend: Admin Categorías

- [x] 4.1 Crear `frontend/src/pages/admin/CategoriasAdminPage.tsx` — tabla con CRUD completo
- [x] 4.2 Conectar con POST/PUT/DELETE /api/v1/categorias/ y refrescar tabla

## 5. Frontend: Admin Clientes

- [x] 5.1 Crear `frontend/src/pages/admin/ClientesAdminPage.tsx` — tabla paginada con búsqueda (nombre, apellido, email, teléfono, activo)

## 6. Frontend: Admin Pedidos

- [x] 6.1 Crear `frontend/src/pages/admin/PedidosAdminPage.tsx` — tabla paginada con filtro por estado y dropdown de transición FSM (solo estados válidos desde estado actual)
- [x] 6.2 Conectar PATCH /api/v1/pedidos/{id}/estado para transiciones

## 7. Routing

- [x] 7.1 Actualizar `frontend/src/router.tsx` — reemplazar placeholders con los componentes reales

## 8. Verificación final

- [x] 8.1 Verificar que `npm run build` compila sin errores (frontend) — 127 modules, 0 errors
- [x] 8.2 Probar Dashboard carga stats correctamente — GET /admin/stats OK: 2 pedidos, $46, 14 productos, 5 clientes
- [x] 8.3 Probar CRUD productos y categorías — endpoints existentes y funcionales
- [x] 8.4 Probar FSM pedidos — transición válida PENDIENTE→CONFIRMADO OK, inválida PENDIENTE→ENTREGADO rechazada ✅
