## Why

El sistema de autenticación funciona pero tiene carencias: no hay endpoint para asignar roles a usuarios (solo se asigna CLIENT automáticamente al registrarse), el rate limiting solo protege login (no otros endpoints sensibles), el refresh token no tiene cola de requests concurrentes, y la navegación del frontend no se adapta al rol del usuario. La especificación exige rate limiting multi-endpoint, navegación por rol, y páginas dedicadas para STOCK y PEDIDOS.

## What Changes

- **Endpoint de asignación de roles**: PUT /api/v1/admin/usuarios/{id}/roles para que ADMIN pueda asignar/modificar roles
- **Frontend UI de roles**: En el CRUD de usuarios del admin, listar roles actuales y permitir agregar/remover
- **Rate limiting multi-endpoint**: Agregar rate limiting a registro (3/hora por IP), creación de pedidos (10/hora por usuario)
- **Refresh token queue**: Implementar cola de requests en el frontend para evitar múltiples refrescos concurrentes cuando varias requests reciben 401 simultáneamente
- **Navegación por rol**: La navbar y el sidebar se adaptan según el rol del usuario (CLIENT, STOCK, PEDIDOS, ADMIN)
- **Página 403 Forbidden**: Ruta dedicada para acceso denegado
- **Página 404**: Ruta dedicada para recurso no encontrado

## Capabilities

### New Capabilities
- `role-assignment-api`: Endpoint para que ADMIN asigne roles a usuarios
- `role-assignment-ui`: Interfaz de gestión de roles en el panel admin

### Modified Capabilities
- `user-auth`: Rate limiting en registro y creación de pedidos. Refresh token queue en frontend
- `admin-panel`: Sección de usuarios con asignación de roles
- `auth-ui`: Navegación adaptada por rol, páginas 403 y 404 dedicadas
- `rbac`: Endpoint para asignación de roles, verificación multi-endpoint rate limiting

## Impact

- **Backend**: Modificar `app/admin/service.py` (asignación de roles), `app/admin/router.py` (nuevo endpoint). Modificar rate limiting config. Agregar dependencia slowapi a más endpoints
- **Frontend**: Refactor `Navbar.tsx` (menú por rol). Agregar página 403, 404. Modificar `apiClient.ts` (cola de refresh). Nueva sección en admin para roles
- **Dependencias nuevas**: Ninguna
