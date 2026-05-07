## 1. Database Models

- [x] 1.1 Create `backend/app/models/usuario.py` — Usuario model with id, nombre, apellido, email (unique, indexed), password_hash, eliminado_en, creado_en, actualizado_en
- [x] 1.2 Create `backend/app/models/refresh_token.py` — RefreshToken model with id, user_id (FK), token_hash (CHAR(64), unique), expires_at, revoked_at, family_id, created_at
- [x] 1.3 Create `backend/app/models/usuario_rol.py` — UsuarioRol association table with usuario_id (FK), rol_id (FK), creado_en, UNIQUE compuesto (usuario_id, rol_id)
- [x] 1.4 Update `backend/app/models/__init__.py` — export Usuario, RefreshToken, UsuarioRol

## 2. Pydantic Schemas

- [x] 2.1 Create `backend/app/auth/schemas.py` — RegisterRequest (nombre, apellido, email, password), LoginRequest (email, password), TokenResponse (access_token, refresh_token, token_type, expires_in), UserResponse (id, nombre, apellido, email, roles), RefreshRequest (refresh_token), LogoutRequest (refresh_token)
- [x] 2.2 Add password validation: min 8 characters, regex-based validation

## 3. Repositories

- [x] 3.1 Create `backend/app/auth/repository.py` — UsuarioRepository extending BaseRepository with get_by_email, get_with_roles methods
- [x] 3.2 Create `backend/app/refreshtokens/repository.py` — RefreshTokenRepository extending BaseRepository with get_by_token_hash, get_active_by_user, revoke_all_by_user, revoke_by_family methods

## 4. Services

- [x] 4.1 Create `backend/app/auth/service.py` — AuthService with register (hash password, assign CLIENT role, generate tokens), login (verify password, generic error, generate tokens), get_user_profile
- [x] 4.2 Create `backend/app/refreshtokens/service.py` — RefreshTokenService with create_token (UUID v4 + SHA-256 hash + family_id), rotate_token (invalidate old, create new, detect replay), revoke_token, handle_replay_attack (revoke all user tokens)

## 5. Routers

- [x] 5.1 Implement `backend/app/auth/router.py` — POST /register, POST /login, GET /me (protected)
- [x] 5.2 Implement `backend/app/refreshtokens/router.py` — POST /refresh, POST /logout
- [x] 5.3 Apply rate limiting decorator (@limiter.limit("5/15minutes")) to login endpoint
- [x] 5.4 Register both routers in `backend/app/main.py` with prefix /api/v1

## 6. Auth Dependencies

- [x] 6.1 Implement `get_current_user` in `backend/app/dependencies.py` — decode JWT, lookup Usuario in BD, return Usuario object with roles
- [x] 6.2 Implement `require_role` in `backend/app/dependencies.py` — verify user has at least one allowed role from usuario_rol table, return 403 if not
- [x] 6.3 Define `CurrentUser` type annotation for dependency injection

## 7. Alembic Migration

- [x] 7.1 Generate Alembic migration for usuario, refresh_token, and usuario_rol tables
- [x] 7.2 Verify migration runs cleanly with `alembic upgrade head`
- [x] 7.3 Verify rollback works with `alembic downgrade -1`

## 8. Security & Configuration

- [x] 8.1 Verify SECRET_KEY in .env is at least 32 characters
- [x] 8.2 Verify bcrypt cost factor is >= 10 in security.py
- [x] 8.3 Ensure login endpoint returns generic error for both invalid email and wrong password

## 9. Verification

- [x] 9.1 Register a new user via POST /api/v1/auth/register and verify 201 + tokens returned
- [x] 9.2 Login with registered user via POST /api/v1/auth/login and verify JWT contains userId, email, roles
- [x] 9.3 Test duplicate email registration returns 409
- [x] 9.4 Test weak password registration returns 422
- [x] 9.5 Test invalid credentials login returns 401 with generic message
- [x] 9.6 Test token refresh via POST /api/v1/auth/refresh — verify old token revoked, new pair issued
- [x] 9.7 Test logout via POST /api/v1/auth/logout — verify refresh token revoked
- [x] 9.8 Test GET /api/v1/auth/me with valid token — verify user data + roles returned
- [x] 9.9 Test GET /api/v1/auth/me without token — verify 401
- [x] 9.10 Test replay attack: use same refresh token twice — verify second attempt revokes all tokens
