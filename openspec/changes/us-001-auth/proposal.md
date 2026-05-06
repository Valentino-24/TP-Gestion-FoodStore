## Why

El sistema necesita autenticación y autorización funcionales para que los usuarios puedan registrarse, iniciar sesión, y acceder a rutas protegidas según su rol. Sin esto, no hay forma de identificar quién hace qué en el sistema. El change setup-infrastructure dejó solo placeholders — este change implementa el sistema completo de auth: registro, login con JWT, refresh tokens con rotación segura, logout, y RBAC.

## What Changes

- Modelo `Usuario` con campos de auditoría, soft delete, y contraseña hasheada con bcrypt
- Modelo `RefreshToken` para almacenamiento seguro en BD con detección de replay attacks
- Tabla intermedia `usuario_rol` (M:N) para roles múltiples por usuario
- Endpoint `POST /api/v1/auth/register` — crea usuario con rol CLIENT automático
- Endpoint `POST /api/v1/auth/login` — valida credenciales, retorna par access + refresh token
- Endpoint `POST /api/v1/auth/refresh` — rota refresh tokens (invalida anterior, emite nuevo)
- Endpoint `POST /api/v1/auth/logout` — revoca refresh token actual
- Endpoint `GET /api/v1/auth/me` — retorna datos del usuario autenticado
- Implementación real de `get_current_user` y `require_role` en dependencies.py
- Rate limiting en login: 5 intentos fallidos por IP en 15 minutos (ya configurado en setup, se aplica aquí)
- Respuesta de login genérica: no diferencia "email no existe" de "contraseña incorrecta"

## Capabilities

### New Capabilities

- `user-auth`: Registro, login, logout, refresh de tokens, y endpoint /me. Incluye JWT access tokens (30 min, HS256) y refresh tokens opacos (7 días) con rotación y detección de replay attacks.
- `rbac`: Verificación de roles desde JWT en endpoints protegidos. Tabla usuario_rol M:N. Factory `require_role()` funcional. Roles fijos: ADMIN, STOCK, PEDIDOS, CLIENT.

### Modified Capabilities

- `backend-app`: Se registran los routers de auth en main.py (ahora hay routers funcionales que montar)
- `auth-dependencies`: `get_current_user` pasa de placeholder a implementación real con lookup en BD. `require_role` verifica roles reales desde la tabla usuario_rol.

## Impact

- **Backend**: Se crean modelos Usuario, RefreshToken, usuario_rol. Se implementan auth/ y refreshtokens/ completos.
- **Database**: 3 tablas nuevas + 1 tabla intermedia. Necesaria migración Alembic.
- **Dependencies.py**: Se reemplazan placeholders con implementación real.
- **Main.py**: Se registran routers de auth y refreshtokens.
- **Frontend**: Los endpoints estarán disponibles para consumo (implementación frontend en change separado).
- **Security**: `.env` con SECRET_KEY es obligatorio — sin él, la app no arranca.
