## Why

El backend de FoodStore está completo con API REST para auth, productos, categorías, clientes, pedidos y pagos, pero no existe ninguna interfaz de usuario. Sin un frontend, la plataforma no es funcional para usuarios reales. Este cambio sienta las bases del frontend para que todos los módulos posteriores (catálogo, carrito, admin, perfil) puedan construirse sobre una base sólida y consistente.

## What Changes

- Crear proyecto **Vite + React + TypeScript** con configuración base
- Implementar **sistema de ruteo** con react-router-dom: público, autenticado y admin
- Crear **cliente API** con axios + interceptors para JWT (access + refresh automático)
- Implementar **auth state management** con Zustand (login, registro, logout, sesión)
- Crear **componentes base**: Layout, ProtectedRoute, AdminRoute, Navbar
- Configurar **TailwindCSS** para estilos
- Conectar con backend existente en `http://localhost:8000/api/v1`

## Capabilities

### New Capabilities
- `frontend-base`: Scaffolding del frontend (Vite + React + TS + TailwindCSS), layouts, routing, componentes base, configuración de build y dev
- `auth-ui`: Flujo de registro/login/logout, auth store con Zustand, API client con interceptors JWT y refresh automático, componentes ProtectedRoute/AdminRoute

### Modified Capabilities
<!-- No se modifican capabilities existentes. Los cambios son frontend puro. -->

## Impact

- Nuevo directorio `frontend/` con proyecto Vite completo
- Dependencias npm: react-router-dom, axios, zustand, tailwindcss, @tailwindcss/vite
- CORS ya configurado en backend para `http://localhost:5173`
- El backend no requiere cambios
