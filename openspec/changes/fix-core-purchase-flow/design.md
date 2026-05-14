## Context

El proyecto tiene el flujo de compra completo implementado a nivel de stores, páginas y APIs, pero tres bugs bloquean su funcionamiento:

1. No existe un botón "Agregar al carrito" en ningún componente del frontend (`ProductCard`, `ProductDetailPage`)
2. El registro de usuario (`AuthService.register()`) no crea automáticamente un registro `Cliente`, por lo que `GET /clientes/me` devuelve 404 post-registro
3. `ProductCard` y `ProductDetailPage` muestran "Cat. {id}" en vez del nombre real de la categoría

El resto de la infraestructura está en su lugar: Zustand store del carrito, hook `useCart()`, hook `useCategories()`, API de categorías, API de clientes.

## Goals / Non-Goals

**Goals:**
- Agregar botón "Agregar al carrito" en `ProductCard` (agrega 1 unidad directo)
- Agregar selector de cantidad + botón "Agregar al carrito" en `ProductDetailPage`
- Crear `Cliente` automáticamente durante el registro de usuario
- Mostrar nombre de categoría en vez del ID en `ProductCard` y `ProductDetailPage`

**Non-Goals:**
- No se modifican endpoints de API ni contracts existentes
- No se agregan nuevas dependencias
- No se toca el carrito store ni la lógica del checkout
- No se implementa la creación de Cliente vía admin (ya existe)
- No se resuelve el catálogo público vs autenticado (se mantiene require auth por ahora)

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| Dónde poner el botón "Agregar" | ProductCard + ProductDetailPage | Solo en detalle | La card permite compra rápida sin entrar al detalle; el detalle permite elegir cantidad |
| Comportamiento en ProductCard | Botón que agrega cantidad=1 directo | Modal de cantidad | Menos fricción; si ya está en carrito incrementa cantidad |
| Cantidad en ProductDetailPage | Input numérico + botón "Agregar al carrito" | Agregar directo | El usuario puede querer múltiples unidades de una |
| Auto-creación de Cliente | Dentro del mismo `UnitOfWork` del registro | Endpoint separado post-registro | Atómico: si falla la creación del cliente, falla el registro completo. Usar email como vínculo. |
| Resolver nombre de categoría | `useCategories()` hook + lookup local en el componente | Endpoint que devuelva categoria_nombre en producto | El hook ya existe y los datos ya están cacheados; no requiere cambios en API de productos |

## Risks / Trade-offs

- **[Riesgo] ProductCard se vuelve dependiente de categorías**: Si `useCategories()` falla, la card muestra "Cat. {id}" como fallback → Aceptable, mismo comportamiento actual
- **[Riesgo] UX del botón en ProductCard**: Un link a detalle + botón "Agregar" puede ser confuso → El botón es visualmente distinto (botón primario vs link de texto)
- **[Trade-off] Auto-creación de Cliente vincula por email**: Si el usuario cambia su email después, el vínculo se pierde → El sistema actual ya usa email como vínculo; cambiarlo requiere un refactor mayor que está fuera de scope
