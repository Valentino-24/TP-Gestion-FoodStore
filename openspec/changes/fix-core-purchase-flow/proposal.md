## Why

El flujo de compra del e-commerce está roto: los usuarios pueden ver productos pero no hay forma de agregarlos al carrito —la `ProductCard` y `ProductDetailPage` no tienen botón "Agregar al carrito". Además, al registrarse nunca se crea el perfil de `Cliente`, por lo que la página de perfil muestra "Sin perfil de cliente" después del registro. Estas son bugs que bloquean la funcionalidad core del sistema.

## What Changes

- **Botón "Agregar al carrito" en ProductCard**: Agregar un botón que llame a `useCart().addItem()` directamente desde la grilla de productos, con cantidad = 1.
- **Botón "Agregar al carrito" en ProductDetailPage**: Agregar selector de cantidad + botón "Agregar al carrito" con la lógica completa.
- **Auto-creación de Cliente al registrarse**: `AuthService.register()` debe crear un registro `Cliente` con los mismos datos (nombre, apellido, email) automáticamente.
- **Mostrar nombre de categoría en vez del ID**: `ProductCard` y `ProductDetailPage` deben resolver el nombre de la categoría y mostrarlo en vez de "Cat. {id}".

## Capabilities

### New Capabilities

<!-- Ninguna — todos los cambios son sobre capacidades existentes -->

### Modified Capabilities

- `product-catalog`: Las páginas de listado y detalle de productos ahora incluyen un botón para agregar items al carrito, y muestran el nombre de la categoría visible en vez del ID numérico.
- `shopping-cart`: El carrito ahora es accesible desde las cards de producto y la página de detalle mediante el botón "Agregar al carrito".
- `user-auth`: El registro de usuario ahora crea automáticamente un registro `Cliente` vinculado por email.

## Impact

- **Frontend**: `ProductCard.tsx`, `ProductDetailPage.tsx` — agregar botón + integración con `useCart()` hook; resolver categoría name via `useCategories()` hook
- **Backend**: `app/auth/service.py` — `register()` ahora crea `Cliente` en la misma transacción
- **Nuevas dependencias**: Ninguna — todo usa infraestructura existente (Zustand store, API de categorías)
- **No rompe flujo existente**: Los cambios son aditivos — no modifican endpoints ni contracts existentes
