## Context

FoodStore ya tiene frontend base (us-005) con auth, layouts, routing y componentes base. El catálogo de productos es la primera página con contenido real. El backend expone `GET /api/v1/productos/` (lista paginada con filtro por categoría) y `GET /api/v1/productos/{id}` (detalle). Ambos endpoints requieren autenticación (Bearer token).

## Goals / Non-Goals

**Goals:**
- Página `/productos` con grilla de productos paginada con datos reales del backend
- Filtro por categoría usando endpoint existente (`?categoria_id=`)
- Paginación funcional con controles (anterior/siguiente + números de página)
- Página `/productos/:id` con detalle completo del producto
- HomePage con sección de productos destacados
- Manejo de estados: loading, empty, error

**Non-Goals:**
- Carrito de compras (us-007)
- Búsqueda por texto (fuera del backlog actual)
- Panel admin de productos (us-008)
- Imágenes de productos (el modelo soporta `imagen_url` pero no hay servicio de imágenes todavía)

## Decisions

### 1. Custom hook `useProducts` para lógica de datos
**Decisión**: Crear `src/hooks/useProducts.ts` que encapsule fetching, paginación, filtrado por categoría y estados (loading, error, data).

**Alternativa**: Hacer fetch directo en el componente — descartado porque la lógica de paginación + filtro + estados se repite y ensucia el componente.

### 2. Componentes separados por responsabilidad
- `ProductCard`: card individual (nombre, precio, categoría, imagen opcional)
- `ProductGrid`: grilla responsive (2-3-4 columnas)
- `Pagination`: controles de paginación reutilizables
- `CategoryFilter`: dropdown para filtrar por categoría

### 3. Fetch en `useEffect` + estado local (sin Zustand)
**Decisión**: Los productos no necesitan estado global. Se fetchan en el componente vía `useEffect` con estado local. Si en el futuro se necesita caché o compartir estado, se puede migrar a React Query o Zustand.

### 4. Diseño responsive con TailwindCSS
**Decisión**: Grilla con `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`. Cards con hover effect, precio destacado, nombre de categoría como badge.

## Risks / Trade-offs

- **[Endpoints requieren auth]** → El catálogo requiere que el usuario esté logueado. Si se quiere hacer público en el futuro, hay que modificar el backend (quitar `current_user` de los endpoints GET de productos).
- **[Sin imágenes reales]** → `imagen_url` es opcional. Las cards muestran un placeholder visual si no hay imagen.
- **[Paginación solo client-side offset]** → El backend maneja page/size, el frontend pasa los parámetros y muestra la info de paginación que devuelve el backend.
