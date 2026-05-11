## Context

El frontend actual tiene rutas para carrito, checkout, pedidos y direcciones, pero no tiene una página de perfil de usuario. El endpoint `GET /api/v1/clientes/me` ya existe y devuelve los datos del cliente autenticado. Sin embargo, no existe un endpoint que permita al usuario CLIENT modificar sus propios datos — `PUT /api/v1/clientes/{id}` solo es accesible para ADMIN.

## Goals / Non-Goals

**Goals:**
- Página `/perfil` que muestre y permita editar nombre, apellido, email y teléfono del usuario autenticado
- Nuevo endpoint `PUT /api/v1/clientes/me` para que el usuario CLIENT actualice su propio perfil
- Enlace a `/perfil` en el Navbar
- Estados de carga, error y vacío en la página de perfil

**Non-Goals:**
- No se toca la página de direcciones (`/perfil/direcciones`) que ya funciona
- No se modifican roles ni permisos existentes
- No se agrega cambio de contraseña (queda para otro cambio)
- No se modifica el endpoint `PUT /api/v1/clientes/{id}` de ADMIN

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| Endpoint para editar perfil propio | `PUT /api/v1/clientes/me` | Ampliar `PUT /{id}` para CLIENT, o crear endpoint separado | No rompe el endpoint existente de ADMIN, es explícito y sigue el patrón de `GET /me` |
| Lógica de negocio | Misma validación que `PUT /{id}` (email único, campos requeridos) | Validación relajada | El CLIENT no debería poder saltarse validaciones que aplican a ADMIN |
| Perfil vs dirección | Página separada en `/perfil` | Unificar en una sola página | Ya existe `/perfil/direcciones` separado, mantener consistencia |
| Formulario | Estado local con React (sin librería externa) | React Hook Form | Es un formulario simple de 4 campos, no justifica una dependencia más |

## Risks / Trade-offs

- [Riesgo] El CLIENT podría no tener un Cliente vinculado (nunca creó perfil) → `GET /me` devuelve 404. Mostrar mensaje claro con opción de crear perfil (o contactar admin).
- [Riesgo] Email único: si el CLIENT cambia su email a uno ya usado por otro cliente → 422. Mostrar error claro en el formulario.
- [Trade-off] No se incluye cambio de contraseña ni avatar. Se deja para un cambio futuro.
