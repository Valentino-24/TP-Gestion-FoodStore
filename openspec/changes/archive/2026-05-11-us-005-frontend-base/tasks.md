## 1. Scaffolding del proyecto

- [x] 1.1 Inicializar proyecto con `npm create vite@latest` (React + TypeScript) en `frontend/`
- [x] 1.2 Instalar dependencias: react-router-dom, axios, zustand
- [x] 1.3 Instalar y configurar TailwindCSS v4 con `@tailwindcss/vite`
- [x] 1.4 Configurar `vite.config.ts` con proxy opcional y puerto 5173
- [x] 1.5 Crear archivo `.env` con `VITE_API_URL=http://localhost:8000/api/v1`
- [x] 1.6 Configurar alias `@/` para imports desde `src/`
- [x] 1.7 Verificar que `npm run dev` y `npm run build` funcionan

## 2. API Client (axios + interceptors)

- [x] 2.1 Crear `src/lib/apiClient.ts` con instancia axios configurada con `baseURL` desde env
- [x] 2.2 Implementar request interceptor que inyecta `Authorization: Bearer <token>` desde localStorage
- [x] 2.3 Implementar response interceptor que captura 401, hace refresh con `POST /refresh`, y reintenta
- [x] 2.4 Implementar cola de requests para evitar N refreshes paralelos (flag `isRefreshing` + cola de pending)

## 3. Auth Store (Zustand)

- [x] 3.1 Crear `src/stores/authStore.ts` con estado: user, accessToken, refreshToken, isAuthenticated, isLoading
- [x] 3.2 Implementar action `login(email, password)` → llama `POST /auth/login`, guarda tokens en localStorage
- [x] 3.3 Implementar action `register(data)` → llama `POST /auth/register`, guarda tokens
- [x] 3.4 Implementar action `logout()` → llama `POST /logout`, limpia localStorage, redirige a /login
- [x] 3.5 Implementar action `hydrate()` → restaura tokens de localStorage, fetchea `GET /auth/me`
- [x] 3.6 Llamar `hydrate()` al inicio de la app para restaurar sesión persistida

## 4. Páginas de autenticación

- [x] 4.1 Crear `src/pages/LoginPage.tsx` con formulario de email + password, validación básica, y conexión a authStore.login()
- [x] 4.2 Crear `src/pages/RegisterPage.tsx` con formulario de nombre + email + password, validación básica, y conexión a authStore.register()
- [x] 4.3 Mostrar errores de API en los formularios (credenciales inválidas, email duplicado, rate limit)
- [x] 4.4 Mostrar estado de carga (loading spinner) mientras se procesa login/register
- [x] 4.5 Redireccionar a / después de login/register exitoso

## 5. Routing y layouts

- [x] 5.1 Crear `src/router.tsx` con react-router-dom: configuración de rutas con layouts anidados
- [x] 5.2 Crear `src/components/LayoutPublic.tsx` — layout centrado minimalista (para login/register)
- [x] 5.3 Crear `src/components/LayoutAuth.tsx` — layout con navbar superior + `<Outlet />`
- [x] 5.4 Crear `src/components/LayoutAdmin.tsx` — layout con sidebar de admin + `<Outlet />`
- [x] 5.5 Crear `src/components/ProtectedRoute.tsx` — verifica auth, redirect a /login si no hay sesión
- [x] 5.6 Crear `src/components/AdminRoute.tsx` — verifica rol ADMIN, redirect a / si no es admin
- [x] 5.7 Crear `src/components/Navbar.tsx` — muestra nombre de usuario + botón de logout
- [x] 5.8 Crear páginas placeholder para rutas futuras: HomePage (vacía con bienvenida), AdminDashboard (vacía)
- [x] 5.9 Configurar `App.tsx` con `<RouterProvider>` y llamada a `hydrate()` al montar

## 6. Verificación final

- [x] 6.1 Verificar que `npm run dev` arranca sin errores
- [x] 6.2 Verificar que `npm run build` produce build exitoso
- [x] 6.3 Verificar que /login y /register son accesibles sin autenticación (rutas públicas en router)
- [x] 6.4 Verificar que rutas protegidas redirigen a /login sin sesión (ProtectedRoute + AdminRoute implementados)
