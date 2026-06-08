## Context

El proyecto FoodStore tiene 11 cambios archivados y 3 activos. La funcionalidad core (auth, catálogo, carrito, checkout con MP real, admin) está implementada y funcional. Sin embargo, la especificación técnica v5.0 (Integrador.txt) define requerimientos arquitectónicos y de features que no están cubiertos:

- TanStack Query para fetching de datos del servidor (hoy se usa `useEffect` + axios directo)
- 4 stores Zustand (hoy existen 2: authStore, cartStore)
- recharts en dashboard (hoy son cards planas)
- HistorialEstadoPedido append-only (no existe)
- Snapshot pattern en pedidos (precio_snapshot, direccion_snapshot)
- Stock decrement/restore atómico (no implementado)
- Feature-Sliced Design (hoy estructura plana)
- Error handling RFC 7807 + error boundary (hoy ad-hoc)

Este cambio toca backend (modelos, servicios) y frontend (stores, hooks, componentes, estructura). Es el cambio más grande del roadmap y es requisito para los siguientes (complete-order-fsm, admin-enhancements, etc.).

## Goals / Non-Goals

**Goals:**
- Implementar TanStack Query como capa única de fetching de datos del servidor
- Implementar los 4 stores Zustand (authStore ✅, cartStore ✅, paymentStore 🆕, uiStore 🆕)
- Agregar gráficos recharts al dashboard admin
- Implementar modelo HistorialEstadoPedido con registro append-only
- Implementar snapshot pattern en pedidos (precio, dirección)
- Implementar stock decrement/restore atómico
- Reorganizar frontend hacia Feature-Sliced Design
- Implementar error handling consistente (backend RFC 7807, frontend error boundary + toasts)
- Expandir tests existentes para cubrir nuevas funcionalidades

**Non-Goals:**
- No se implementa el módulo de ingredientes (es `ingredients-module`, siguiente en roadmap)
- No se implementa la máquina de estados completa con timeline visual (es `complete-order-fsm`)
- No se implementa CRUD de usuarios con roles (es `admin-enhancements` y `enhance-auth-rbac`)
- No se modifica la lógica de negocio existente de auth, productos, categorías, clientes
- No se toca la integración con MercadoPago (ya funcional en `mp-integration`)

## Decisions

### D1: TanStack Query v5 con hooks por dominio

**Decisión**: Usar `@tanstack/react-query` v5 con hooks personalizados agrupados por dominio (`useProductos`, `usePedidos`, `useAuth`, `useAdmin`).

**Alternativas consideradas**:
- **RTK Query**: Demasiado overhead para el tamaño del proyecto, opinión fuerte sobre estructura de store
- **SWR**: Menos features que TanStack Query (sin mutations optimistas, sin query devtools)
- **useEffect + axios directo**: Actual — sin caché, sin revalidación, sin estados de carga/error consistentes

**Rationale**: TanStack Query v5 es el estándar del ecosistema React para fetching. Provee caché automático, revalidación en background, mutations con invalidación, loading/error states, y DevTools. La especificación lo menciona explícitamente.

```
┌─────────────────────────────────────────────────────┐
│                   Componentes React                  │
├─────────────────────────────────────────────────────┤
│  useProductos() │ usePedidos() │ useAuth() │ ...    │  ← Hooks por dominio
├─────────────────────────────────────────────────────┤
│              @tanstack/react-query                   │  ← Caché + fetching
├─────────────────────────────────────────────────────┤
│              apiClient (axios)                       │  ← HTTP con interceptors
└─────────────────────────────────────────────────────┘
```

### D2: 4 stores Zustand con persistencia selectiva

**Decisión**: Implementar los 4 stores según la especificación:

| Store | Estado | Persiste | Middleware |
|-------|--------|----------|-----------|
| authStore | accessToken, user, isAuthenticated | Solo accessToken | persist |
| cartStore | items[], totalItems, subtotal | items completos | persist |
| paymentStore | status, mpPaymentId, errorDetail | No | — |
| uiStore | theme, sidebarOpen, toasts[] | Solo theme | persist |

**Rationale**: La separación entre TanStack Query (datos del servidor) y Zustand (estado del cliente) es arquitectónica. Mezclarlos en un solo store es un antipatrón según la especificación.

### D3: HistorialEstadoPedido como modelo independiente con inserción única

**Decisión**: Modelo SQLModel separado con tabla `historial_estado_pedido`. Solo INSERT — nunca UPDATE/DELETE.

```python
class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"
    
    id: int = Field(primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_desde: str | None = None  # NULL para transición inicial
    estado_hasta: str
    usuario_id: int | None = None  # NULL = sistema
    observacion: str | None = None
    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Registro**: Cada transición de estado llama a `HistorialEstadoRepository.create()` dentro del mismo UoW que el cambio de estado.

### D4: Snapshot pattern en pedidos

**Decisión**: Al crear un pedido, capturar `precio_snapshot` en cada DetallePedido y `direccion_snapshot` como JSON en Pedido.

**Campos actuales a modificar**:
- `DetallePedido.precio_unitario` → pasa a llamarse `precio_snapshot` semánticamente (el valor ya se captura al crear)
- `Pedido` → agregar `direccion_snapshot: str | None` (JSON serializado de la dirección)

**Rationale**: Los precios y direcciones cambian con el tiempo. Sin snapshots, un pedido histórico mostraría datos incorrectos. La especificación lo exige explícitamente (RN-04, RN-DA06).

### D5: Stock management atómico con SELECT FOR UPDATE

**Decisión**: Usar `SELECT ... FOR UPDATE` dentro de una transacción UoW para evitar race conditions.

```python
async def decrement_stock(self, producto_id: int, cantidad: int) -> None:
    producto = await self.session.execute(
        select(Producto).where(Producto.id == producto_id).with_for_update()
    )
    producto = producto.scalar_one_or_none()
    if not producto or producto.stock_cantidad < cantidad:
        raise HTTPException(400, "Stock insuficiente")
    producto.stock_cantidad -= cantidad
```

**Alternativa considerada**: `UPDATE ... SET stock = stock - :cant WHERE id = :id AND stock >= :cant` — más performante pero no permite validaciones adicionales ni registro en historial.

### D6: Feature-Sliced Design progresivo

**Decisión**: Reorganizar el frontend de a una capa por vez, empezando por `shared/` y `entities/`, sin romper la funcionalidad existente.

```
src/
├── shared/          # UI base, apiClient, types, constants
│   ├── ui/          # Button, Input, Modal, Toast, Skeleton
│   ├── api/         # apiClient, interceptors
│   └── types/       # tipos globales (Pago, Pedido, etc.)
├── entities/        # modelos de dominio + hooks TanStack Query
│   ├── producto/    # types, useProductos, ProductCard
│   ├── pedido/      # types, usePedidos, OrderTimeline
│   └── auth/        # types, useAuth, ProtectedRoute
├── features/        # interacciones de usuario
│   ├── cart/        # CartDrawer, useCart (Zustand)
│   └── checkout/    # CheckoutForm, AddressSelector
├── widgets/         # composiciones de features
│   ├── ProductGrid
│   └── AdminLayout
└── pages/           # rutas
    ├── LoginPage
    ├── ProductListPage
    └── admin/...
```

**Estrategia**: No mover archivos de golpe. Crear la estructura nueva, migrar imports progresivamente.

### D7: Error handling con RFC 7807 + error boundary global

**Decisión Backend**: Middleware FastAPI que captura excepciones y las formatea como Problem Details (RFC 7807).

```json
{
  "type": "/errors/validation-error",
  "title": "Error de validación",
  "status": 422,
  "detail": "El campo email no es válido",
  "instance": "/api/v1/auth/register",
  "errors": [{"field": "email", "message": "Email inválido"}]
}
```

**Decisión Frontend**: ErrorBoundary React a nivel de Layout + ToastStore para errores no fatales.

## Risks / Trade-offs

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| [R1] Migración a TanStack Query rompe componentes existentes | Media | Migrar por dominio, no todo junto. Tests existentes validan |
| [R2] Reorganización FSD confusa si se hace de golpe | Alta | Hacerlo progresivo: shared → entities → features → widgets → pages. Cada paso funcional |
| [R3] SELECT FOR UPDATE puede causar deadlocks | Baja | Usar orden consistente de locks (siempre por producto_id ASC). Timeout configurable |
| [R4] HistorialEstadoPedido append-only puede crecer mucho | Baja (volumen del TP) | No requiere solución ahora. Para producción: particionado por fecha |
| [R5] RFC 7807 cambia formato de error actual — frontend debe adaptarse | Media | El frontend ya parsea errores con try/catch. Migrar el interceptor de axios para manejar el nuevo formato |
| [R6] Breaking: TanStack Query requiere cambios en tests existentes | Media | Los tests de stores y componentes no se ven afectados. Los tests de integración (HTTP) tampoco. Solo los tests de hooks si existieran |
