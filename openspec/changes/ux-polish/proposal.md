## Why

La experiencia de usuario actual es funcional pero carece de refinamientos que marcan la diferencia en la calidad percibida: no hay sistema de toasts/notificaciones, los estados de carga usan spinners genéricos, faltan estados vacíos ilustrados, no hay modo oscuro, y la experiencia mobile no está pulida. Estas mejoras elevan la calidad del proyecto y suman puntos en la rúbrica de UI/UX.

## What Changes

- **Sistema de toasts**: Implementar sistema de notificaciones global con ToastStore (Zustand) para feedback no bloqueante (éxito, error, advertencia, info)
- **Loading skeletons**: Reemplazar spinners por skeletons con placeholder shimmer en cards de productos, tablas admin, detalle de pedido
- **Modo oscuro**: Implementar theme toggle (light/dark) con persistencia en localStorage a través de uiStore. Aplicar clases dark: en Tailwind
- **Página 404 personalizada**: Diseñar página 404 con ilustración y enlaces útiles
- **Estados vacíos**: Diseñar componentes EmptyState reutilizables para todas las listas vacías (carrito, pedidos, direcciones, productos)
- **Responsive**: Ajustes de layout mobile para todas las páginas principales
- **Debounce en búsqueda**: Agregar debounce de 300ms en el input de búsqueda de productos
- **Animaciones sutiles**: Transiciones suaves en hover, focus, y cambios de estado usando Tailwind transitions

## Capabilities

### New Capabilities
- `toast-system`: Sistema global de notificaciones toast con Zustand store + componente ToastContainer
- `theme-switcher`: Sistema de tema oscuro/claro con persistencia en uiStore
- `empty-state`: Componente EmptyState reutilizable para estados vacíos

### Modified Capabilities
- `frontend-base`: Agregar ToastContainer en Layout, theme classes condicionales
- `product-catalog`: Skeletons en ProductGrid, debounce en búsqueda
- `orders-history`: Skeletons en lista de pedidos, EmptyState para sin pedidos
- `shopping-cart`: EmptyState para carrito vacío
- `admin-panel`: Skeletons en tablas admin

## Impact

- **Frontend**: Nuevos componentes `Toast.tsx`, `Skeleton.tsx`, `EmptyState.tsx`, `ThemeToggle.tsx`. Modificar `uiStore.ts` (toasts, theme). Modificar layouts para soportar dark mode. Modificar páginas para usar skeletons y empty states
- **Backend**: Sin cambios
- **Dependencias nuevas**: Ninguna (todo con TailwindCSS + React existente)
