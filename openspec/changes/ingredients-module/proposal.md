## Why

La especificación técnica v5.0 define ingredientes y alérgenos como parte central del catálogo de productos (US-011 a US-014, US-017, US-019, US-023). Actualmente no existe el modelo Ingrediente, ni la relación M2M ProductoIngrediente, ni la visualización de alérgenos en el frontend. Esto es una funcionalidad requerida por la rúbrica y por las historias de usuario.

## What Changes

- **Modelo Ingrediente**: Crear tabla `ingrediente` con campos: id, nombre (unique), descripcion, es_alergeno (boolean), activo, creado_en, actualizado_en, eliminado_en
- **Tabla ProductoIngrediente**: Relación M2M entre producto e ingrediente con campo `es_removible` para personalización
- **Backend CRUD**: Endpoints REST completos para ingredientes (POST, GET, PUT, DELETE) con soft-delete
- **Backend asociación**: Endpoints para asociar/desasociar ingredientes a productos (POST/DELETE /api/v1/productos/{id}/ingredientes/{ing_id})
- **Frontend Admin CRUD**: Página de gestión de ingredientes en el panel admin
- **Frontend detalle producto**: Mostrar ingredientes con badge de alérgeno en la página de detalle
- **Frontend filtro**: Filtrar productos excluyendo alérgenos específicos

## Capabilities

### New Capabilities
- `ingredients-api`: CRUD completo de ingredientes con soft-delete y flag de alérgeno
- `ingredients-admin-ui`: Página de gestión de ingredientes en el panel de administración

### Modified Capabilities
- `product-catalog`: Agregar ingredientes al detalle de producto con badge de alérgeno. Agregar filtro por exclusión de alérgenos
- `product-catalog`: Endpoint de detalle debe incluir ingredientes con sus flags

## Impact

- **Backend**: Nuevo módulo `app/ingredientes/` con model, schemas, repository, service, router. Modificar `app/productos/` para incluir endpoints de asociación. Agregar migración Alembic
- **Frontend**: Nueva página `admin/IngredientesAdminPage.tsx`. Modificar `ProductDetailPage.tsx` para mostrar ingredientes. Modificar `ProductListPage.tsx` para filtro por alérgenos
- **Seed data**: Posibles ingredientes iniciales (harina, lactosa, huevo, maní, etc.)
- **Dependencias nuevas**: Ninguna
