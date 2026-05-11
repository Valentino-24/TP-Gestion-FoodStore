## Context

FoodStore tiene un backend completo con API REST, autenticación JWT con refresh tokens, RBAC, y CRUDs para todas las entidades. No existe frontend alguno. Este cambio construye el frontend base desde cero.

**Stack elegido**: Vite + React 18 + TypeScript + TailwindCSS v4 + react-router-dom v7 + Zustand + axios.

**Backend**: corre en `http://localhost:8000/api/v1` con CORS habilitado para `http://localhost:5173`.

## Goals / Non-Goals

**Goals:**
- Scaffolding del proyecto frontend con Vite, React, TypeScript y TailwindCSS
- Sistema de routing con separación de rutas públicas, autenticadas y de admin
- Cliente API con axios + interceptor que maneje automáticamente refresh de tokens y redirect a login si expiró
- Auth store con Zustand que gestione login, registro, logout y estado de sesión
- Componentes base reutilizables: Layout, Navbar, ProtectedRoute, AdminRoute

**Non-Goals:**
- Páginas de catálogo de productos, carrito, checkout o pedidos (son changes separados)
- Panel admin con CRUDs y dashboard (us-008)
- Perfil de usuario y direcciones (us-009)
- Tests automatizados (us-011)
- Dockerización (us-010)

## Decisions

### 1. Vite + React + TypeScript + TailwindCSS
**Decisión**: Vite como bundler por su velocidad en dev con HSM nativo. React 18 con TypeScript. TailwindCSS v4 con el plugin `@tailwindcss/vite` para styling utility-first.

**Alternativa considerada**: Next.js — descartado porque no necesitamos SSR/SSG, y Vite es más simple para SPA pura.

### 2. Zustand sobre Context API o Redux
**Decisión**: Zustand para auth state management. Liviano, sin boilerplate, con persistencia opcional (localStorage para tokens).

**Alternativa considerada**: Redux Toolkit — excesivo para el estado que manejamos (solo auth). Context API — puede causar re-renders innecesarios y es más verboso para actualizaciones frecuentes de token.

### 3. Axios con interceptores para JWT
**Decisión**: Axios instance centralizada con request interceptor que inyecta el token y response interceptor que captura 401 y hace refresh automático antes de reintentar.

**Alternativa considerada**: fetch nativo — requiere wrapear manualmente la lógica de refresh, sin interceptors.

### 4. Rutas con react-router-dom v7
**Decisión**: Layout anidado con `<Outlet />`: layout público (login/register), layout autenticado (navbar + sidebar + contenido), layout admin (solo ADMIN).

**Estructura**:
```
/             → Layout público (redirect a /productos si autenticado)
/login        → LoginPage
/register     → RegisterPage
/*            → LayoutAuth (ProtectedRoute) → Outlet
  /productos  → Catálogo (us-006)
  /carrito    → Carrito (us-007)
  /perfil     → Perfil (us-009)
  /admin/*    → LayoutAdmin (AdminRoute) → Outlet
    /admin/productos   → CRUD productos (us-008)
    /admin/categorias  → CRUD categorías (us-008)
    /admin/clientes    → CRUD clientes (us-008)
    /admin/pedidos     → Gestión pedidos (us-008)
```

### 5. Componentes base separados por responsabilidad
- **ApiClient**: axios instance con interceptors (singleton)
- **AuthStore**: Zustand store con actions login/register/logout/refresh
- **ProtectedRoute**: verifica token, redirect a /login si no autenticado
- **AdminRoute**: verifica rol ADMIN, redirect a / si no tiene permisos
- **Layout**: navbar superior + sidebar lateral (opcional) + `<Outlet />`

## Risks / Trade-offs

- **[Persistencia de tokens]** → Almacenar access_token y refresh_token en localStorage. Si hay ataque XSS, los tokens pueden ser robados. Aceptado por ser SPA sin httpOnly cookies (el backend no emite cookies, solo JSON).
- **[Refresh token expirado durante navegación]** → El interceptor detecta 401 → intenta refresh → si falla, limpia store y redirige a /login. El usuario pierde estado pero no crashea la app.
- **[Múltiples requests 401 simultáneos]** → El interceptor usa un flag `isRefreshing` y encola los requests fallidos mientras refresca, para no disparar N refreshes paralelos.
