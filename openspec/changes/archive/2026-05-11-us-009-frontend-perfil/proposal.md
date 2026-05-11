## Why

Los usuarios registrados no tienen una página de perfil donde puedan ver y editar sus datos personales (nombre, apellido, email, teléfono). Actualmente el frontend tiene direcciones (`/perfil/direcciones`) pero falta la página principal de perfil y el navbar no tiene acceso directo a ella.

## What Changes

- **Nueva página `/perfil`** que muestra los datos del perfil del usuario con formulario editable
- **Nuevo endpoint `PUT /api/v1/clientes/me`** que permite al usuario autenticado actualizar su propio perfil (hoy solo ADMIN puede modificar clientes)
- **Navbar actualizado** con enlace al perfil del usuario
- **Ruta `/perfil` agregada** al router de frontend

## Capabilities

### New Capabilities
- `user-profile`: Página de perfil de usuario con visualización y edición de datos personales (nombre, apellido, email, teléfono), vinculada al endpoint `GET /api/v1/clientes/me` y al nuevo `PUT /api/v1/clientes/me`

### Modified Capabilities
<!-- No existing specs change — user-profile es nueva, y la modificación al endpoint PUT /me es implementación del backend que no cambia specs existentes -->

## Impact

- **Frontend**: Nueva página `ProfilePage.tsx`, nuevo enlace en Navbar, nueva ruta en router
- **Backend**: Nuevo endpoint `PUT /api/v1/clientes/me` en el router de clientes (permite al CLIENT autenticado modificar su propio perfil)
- **No rompe cambios existentes**
