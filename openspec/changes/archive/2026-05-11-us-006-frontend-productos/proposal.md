## Why

El frontend base ya está funcionando con auth y layouts, pero no hay contenido real. Los usuarios no pueden ver ni explorar los productos del catálogo. Este cambio implementa la visualización pública del catálogo de productos, que es la funcionalidad principal del negocio y el punto de entrada para que los clientes comiencen a comprar.

## What Changes

- Crear **página de catálogo** en `/productos` con grilla de productos paginada
- Crear **página de detalle** en `/productos/:id` con info completa del producto
- Implementar **filtro por categoría** en el catálogo (dropdown o sidebar)
- Implementar **paginación** con controles (anterior/siguiente + números)
- Mejorar la **HomePage** con productos destacados y navegación al catálogo
- Conectar con los endpoints existentes: `GET /productos/` y `GET /productos/{id}`

## Capabilities

### New Capabilities
- `product-catalog`: Catálogo frontend de productos con grilla, paginación, filtro por categoría, y página de detalle

### Modified Capabilities
<!-- No se modifican capabilities existentes. frontend-base ya define la ruta /productos como placeholder. -->

## Impact

- Archivos nuevos en `frontend/src/pages/`: `ProductListPage.tsx`, `ProductDetailPage.tsx`
- Archivos nuevos en `frontend/src/components/`: `ProductCard.tsx`, `ProductGrid.tsx`, `Pagination.tsx`, `CategoryFilter.tsx`
- Posible nuevo hook: `frontend/src/hooks/useProducts.ts`
- HomePage actualizada para mostrar productos destacados
- Router actualizado: la ruta `/productos` deja de ser placeholder
- No requiere cambios en backend
