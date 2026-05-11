## Context

El change setup-infrastructure dejó la base: FastAPI corriendo, SQLModel async, BaseRepository genérico, UnitOfWork, y placeholders para auth. Los skeletons de `auth/` y `refreshtokens/` existen pero sin implementación. `dependencies.py` tiene `get_current_user` y `require_role` como placeholders que retornan datos ficticios.

Los docs del proyecto definen el stack y las reglas de negocio con precisión: JWT HS256 (30 min access, 7 días refresh), bcrypt cost >= 10, rotación de refresh tokens, detección de replay attacks, rate limiting en login (5/15min), 4 roles fijos con tabla M:N.

## Goals / Non-Goals

**Goals:**
- Modelos SQLModel para Usuario, RefreshToken, y tabla intermedia usuario_rol
- Endpoints funcionales: register, login, refresh, logout, me
- `get_current_user` real que hace lookup en BD
- `require_role` funcional que verifica roles desde BD
- Refresh tokens con rotación y detección de replay attacks (family_id)
- Migración Alembic para las 3 tablas nuevas
- Respuesta de login genérica por seguridad

**Non-Goals:**
- No implementar cambio de contraseña (US-063 — change futuro)
- No implementar forgot password / reset (US-074 — change futuro)
- No implementar gestión de roles admin (US-054 — change futuro)
- No implementar frontend auth (stores Zustand, forms, interceptors — change frontend)
- No implementar validación de email por link (no está en los requisitos)

## Decisions

### D1: Usuario model en `app/models/usuario.py`
**Decision**: El modelo Usuario va en `app/models/` siguiendo la convención existente de Rol, EstadoPedido, FormaPago.
**Rationale**: Los modelos de dominio comparten la misma Base y se importan desde `models/__init__.py`. Los skeletons en `auth/model.py` quedan como referencia vacía o se eliminan.
**Alternativas consideradas**:
- Ponerlo en `auth/model.py`: Roto la convención establecida en `models/`
- Ambos: Duplicación innecesaria

### D2: RefreshToken con SHA-256 hash + family_id
**Decision**: Almacenar SHA-256 del refresh token (nunca el token en texto plano). Cada token tiene un `family_id` UUID para detectar rotaciones y replay attacks.
**Rationale**: Si la BD se filtra, los tokens hash no son utilizables. El family_id permite detectar cuando un refresh token ya usado se reutiliza (se revocan todos los tokens de esa familia).
**Alternativas consideradas**:
- Almacenar token opaco sin hash: Vulnerable si hay SQL injection o backup expuesto
- Solo expiración sin family_id: No se detecta replay attacks

### D3: Tabla usuario_rol como M:N explícita
**Decision**: Tabla intermedia `usuario_rol` con campos (usuario_id, rol_id, creado_en) con UNIQUE compuesto.
**Rationale**: Un usuario puede tener múltiples roles. La tabla explícita permite auditoría de cuándo se asignó cada rol.
**Alternativas consideradas**:
- Campo JSON en Usuario: Más simple pero pierde integridad referencial y auditabilidad
- Array de roles en Usuario: No soporta FK a tabla Rol

### D4: Password hashing en Service layer
**Decision**: El hash de contraseña se aplica en `AuthService`, no en el modelo ni en el repository.
**Rationale**: El modelo es puro (solo datos). El service es el lugar correcto para lógica de negocio como hashing. Sigue el patrón Router → Service → UoW → Repository.
**Alternativas consideradas**:
- Hash en el modelo con validator SQLModel: Acopla modelo a bcrypt
- Hash en el router: Mezcla lógica de negocio con transporte

### D5: `get_current_user` retorna objeto Usuario, no dict
**Decision**: Implementar una clase `UserContext` (o usar el modelo Usuario directamente) como retorno de `get_current_user`.
**Rationale**: El placeholder retorna `dict`. Para type safety y claridad, necesitamos un tipo concreto que incluya id, email, y roles.
**Alternativas consideradas**:
- Mantener dict: Sin type checking, propenso a errores
- Pydantic model: Overhead para un objeto interno

### D6: Registro retorna tokens inmediatamente
**Decision**: El endpoint POST /auth/register retorna el par access + refresh token tras crear la cuenta (mismo flujo que login).
**Rationale**: Mejora UX — el usuario queda logueado tras registrarse sin step adicional. Es el patrón definido en los criterios de US-001.
**Alternativas consideradas**:
- Solo crear cuenta, requerir login separado: UX inferior, step extra

### D7: Soft delete en Usuario
**Decision**: Usuario tiene `eliminado_en: Optional[datetime]` para soft delete.
**Rationale**: Coherente con la regla RN de soft delete global. Permite recuperación y auditoría.
**Alternativas consideradas**:
- Hard delete: Viola la convención del proyecto

## Risks / Trade-offs

- **[Risk]** JWT stateless: access token no se puede revocar antes de expiración → **Mitigation**: Window de 30 min es aceptable. Para logout inmediato, se podría mantener blacklist de tokens, pero agrega complejidad. El logout revoca el refresh token, que es suficiente para prevenir nuevas sesiones.
- **[Risk]** Family_id para replay detection es complejo de testear → **Mitigation**: Tests unitarios específicos con mock de tokens. La lógica está aislada en el service.
- **[Risk]** bcrypt con cost >= 10 puede ser lento en desarrollo → **Mitigation**: Aceptable. El cost 10 toma ~100ms por hash, no impacta UX en login/register.
- **[Risk]** Tabla usuario_rol puede tener datos inconsistentes si no se usa UoW → **Mitigation**: Todas las operaciones de role assignment usan UnitOfWork para atomicidad.
- **[Risk]** `get_current_user` hace query en BD en cada request protegido → **Mitigation**: Se puede cachear con `@lru_cache` por request lifetime o usar el payload del JWT como fuente primaria y BD como fallback para roles.
