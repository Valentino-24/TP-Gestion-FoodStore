## Context

El frontend de FoodStore tiene un layout admin funcional (`LayoutAdmin.tsx`) con sidebar y 5 rutas placeholder (`/admin`, `/admin/productos`, `/admin/categorias`, `/admin/clientes`, `/admin/pedidos`) que actualmente renderizan todas el mismo componente vacío. El backend tiene APIs completas para productos, categorías, clientes y pedidos — todas soportan operaciones admin (CRUD completo, FSM para pedidos). Solo falta el frontend.

**Stack frontend**: Vite + React + TS + TailwindCSS v4 + Zustand + axios con interceptors JWT
**Stack backend**: FastAPI + SQLModel + SQLAlchemy async + estructuras feature-first

## Goals / Non-Goals

**Goals:**
- Crear endpoint `GET /api/v1/admin/stats` que devuelva métricas del dashboard
- Reemplazar Dashboard placeholder con cards de estadísticas (pedidos hoy, ingresos hoy, total productos, clientes activos)
- Implementar página `/admin/productos` con tabla paginada, búsqueda, modal de edición/creación, y soft-delete
- Implementar página `/admin/categorias` con tabla y CRUD completo (crear, editar, soft-delete)
- Implementar página `/admin/clientes` con listado paginado y detalle por ID
- Implementar página `/admin/pedidos` con listado paginado, filtro por estado, y dropdown de transición FSM

**Non-Goals:**
- Roles STOCK/PEDIDOS — el panel es solo para ADMIN
- Notificaciones push/email
- Exportación de datos (CSV/Excel)
- Gráficos/Charts avanzados — cards con números bastan

## Decisions

### 1. Dashboard stats endpoint
**Decisión**: Crear `backend/app/admin/router.py` con `GET /admin/stats` que consulta counts directamente desde los repositorios existentes (pedidos de hoy, ingresos de hoy, total productos activos, total clientes activos). No se necesita modelo nuevo ni tabla — son queries agregadas.

**Alternativa**: Consultar desde el frontend cada API por separado — descartado (N+1 requests, inconsistencias por timing).

### 2. Tabla admin reutilizable
**Decisión**: No crear un componente `AdminTable` genérico. Cada página admin tiene su propia tabla con JSX específico. La repetición es preferible a una abstracción prematura que no conocemos todavía.

**Alternativa**: Tabla genérica con props de columnas — descartado porque cada CRUD tiene interacciones distintas (modal de edición vs dropdown de estado vs detalle).

### 3. Pedido FSM desde frontend
**Decisión**: El dropdown de estado en pedidos muestra solo las transiciones válidas desde el estado actual (no todos los estados posibles). Al seleccionar una transición, se llama `PATCH /api/v1/pedidos/{id}/estado`. Si la transición es inválida, el backend rechaza con 400.

**Alternativa**: Enviar cualquier estado y dejar que el backend rechace — descartado porque es mejor UX mostrar solo opciones válidas.

### 4. Estado local sin store global
**Decisión**: Cada página admin maneja su propio estado con `useState` + `useEffect` y fetches directos con `apiClient`. No se necesita Zustand store compartido porque las páginas no comparten estado entre sí.

**Alternativa**: Store global admin — descartado (overengineering para este alcance).

## Risks / Trade-offs

- **[Dashboard stats endpoint nuevo]** → Es un solo endpoint simple, bajo riesgo. Si el sistema crece, migrar a un módulo de analytics dedicado.
- **[Tablas sin componente reutilizable]** → Si aparecen más CRUDs admin (ej. cupones), considerar refactor a tabla genérica. Por ahora mantener específico.
- **[Hardcode de transiciones FSM en frontend]** → Las transiciones válidas están duplicadas (backend model + frontend). Si cambian, hay que actualizar ambos lados. Alternativa futura: endpoint `GET /api/v1/pedidos/transiciones` que devuelva las transiciones válidas según estado actual.
