## 1. Backend — Endpoint PUT /api/v1/clientes/me

- [x] 1.1 Add `PUT /api/v1/clientes/me` endpoint in `backend/app/clientes/router.py` que permita al usuario autenticado (CLIENT) actualizar su propio perfil usando `ClienteUpdate` schema y vinculación por email
- [x] 1.2 Verificar que el endpoint valida email único: rechaza con 422 si el nuevo email ya pertenece a otro cliente
- [x] 1.3 Verificar que el endpoint retorna 404 si el usuario autenticado no tiene un cliente vinculado

## 2. Frontend — ProfilePage component

- [x] 2.1 Crear `frontend/src/pages/ProfilePage.tsx` con fetch de `GET /api/v1/clientes/me` y display de datos (nombre, apellido, email, teléfono) con estados: loading (skeleton), error (mensaje + retry), y 404 (mensaje "sin perfil")
- [x] 2.2 Agregar modo edición: formulario inline con campos nombre, apellido, email, teléfono, botones "Guardar" y "Cancelar"
- [x] 2.3 Implementar `PUT /api/v1/clientes/me` al guardar, mostrar feedback de éxito/error (incluyendo 422 por email duplicado)
- [x] 2.4 Manejar cancelación: revertir a datos originales sin recargar

## 3. Frontend — Router y Navbar

- [x] 3.1 Agregar ruta `{ path: '/perfil', element: <ProfilePage /> }` en el router (dentro de LayoutAuth)
- [x] 3.2 Agregar enlace "Mi Perfil" en el Navbar (junto a "Mis Pedidos" y cerrar sesión)
