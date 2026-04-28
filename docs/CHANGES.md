# Changes — Qué son y cómo trabajar con ellos

## ¿Qué es un change?

Un **change** es la unidad mínima de trabajo en el flujo SDD. No es una tarea suelta ni un ticket — es un conjunto de tres artefactos que juntos describen, diseñan e implementan una funcionalidad del sistema de forma completa y trazable.

Cada change tiene su propia carpeta dentro de `openspec/changes/` y contiene exactamente estos tres archivos:

```
openspec/changes/nombre-del-change/
├── proposal.md   ← QUÉ se va a construir y POR QUÉ
├── design.md     ← CÓMO técnicamente (arquitectura, modelos, endpoints)
└── tasks.md      ← CHECKLIST atómica de implementación
```

Una vez que el change está completamente implementado y verificado, se **archiva**: las specs se sincronizan en `openspec/specs/` y la carpeta del change se mueve al historial. Esa documentación viva queda disponible para todos los changes futuros.

---

## ¿Para qué sirve?

- **Trazabilidad**: cada línea de código tiene una propuesta y un diseño que la justifica.
- **Revisión antes de implementar**: el diseño se aprueba en papel antes de que el agente escriba una sola línea de código. Un error en el diseño cuesta 0. El mismo error en código cuesta horas de refactor.
- **Contexto persistente**: cuando el agente empieza un nuevo change, lee las specs de los changes anteriores ya archivados. Sabe qué existe, qué patrones se usaron, y no propone código duplicado o inconsistente.
- **Documentación automática**: al terminar el proyecto, `openspec/specs/` es la documentación completa del sistema. No hay que escribirla por separado.

---

## ¿Cómo se generan?

Los changes **no se crean a mano** — los genera el agente a partir de los documentos del proyecto y las historias de usuario. El flujo es siempre el mismo:

### 1. Explorar (opcional)
Antes de proponer, podés pedirle al agente que piense y analice el problema:
```
/opsx:explore [tema o pregunta]
```
El agente investiga el codebase y razona con vos. No genera código ni toma compromisos. Útil cuando no tenés claro cómo encaja algo en la arquitectura.

### 2. Proponer
Le pedís al agente que genere los tres artefactos del change:
```
/opsx:propose [nombre-del-change]
```
El agente lee los documentos en `docs/`, las historias de usuario relevantes y las specs ya archivadas. Genera `proposal.md`, `design.md` y `tasks.md`.

**Antes de continuar, revisás los artefactos.** Verificás que:
- El diseño respeta la arquitectura en capas (Router → Service → UoW → Repository → Model)
- Las tareas son atómicas (horas, no días)
- Las reglas de negocio están reflejadas
- El stack tecnológico es el correcto

Si algo está mal, lo corregís antes de implementar.

### 3. Aplicar
Una vez aprobados los artefactos, el agente implementa tarea por tarea:
```
/opsx:apply [nombre-del-change]
```
El agente lee `design.md` y `tasks.md`, implementa cada tarea en orden y la marca como completada. No improvisa — sigue el plan.

### 4. Archivar
Cuando todas las tareas están completas y los tests pasan:
```
/opsx:archive [nombre-del-change]
```
Las specs se sincronizan, el change se mueve al historial y el próximo change ya puede usarlas como contexto.

---

## ¿Cómo saber qué changes crear para este proyecto?

Los changes **no están predefinidos** — son una decisión de diseño que tomás vos basándote en los documentos del sistema.

El primer paso es pedirle al agente que analice los tres documentos de `docs/` y proponga el mapa completo de changes: cuáles son, en qué orden deben implementarse y por qué.

```
Analizá los documentos en docs/ y proponé el mapa completo 
de changes para desarrollar Food Store. Para cada change indicá:
- nombre sugerido
- qué funcionalidad cubre
- qué historias de usuario implementa
- de qué otros changes depende y por qué
```

Revisás la propuesta, la discutís, la ajustás si hace falta — y recién entonces empezás con el primer `/opsx:propose`.

---

## Reglas importantes

- **Nunca implementes sin artefactos.** Si no existe `proposal.md` y `design.md` aprobados, no hay `/opsx:apply`.
- **El orden importa.** Si el change B necesita código del change A, A tiene que estar archivado antes de proponer B.
- **Un change = un commit** (o varios commits atómicos). Nunca mezcles dos changes en un mismo commit.
- **Las specs son código.** Se versionan en git, se revisan en PRs, evolucionan con el proyecto.

---

## Mapa de Changes — Food Store E-Commerce

### change: setup-infrastructure

**Descripción**: Scaffolding completo del backend: FastAPI, SQLModel, PostgreSQL, Alembic, seed data, patrones base (BaseRepository, Unit of Work, get_current_user, require_role).

**Historias de usuario**: US-000, US-000a, US-000b, US-000d, US-068, US-074

**Dependencias**: Ninguna (es la fundación)

---

### change: setup-frontend

**Descripción**: Scaffolding completo del frontend: React + TypeScript + Vite, Zustand stores (auth, cart, payment, ui), TanStack Query, Axios con interceptores, routing base.

**Historias de usuario**: US-000c, US-000e, US-066, US-067

**Dependencias**: setup-infrastructure

---

### change: auth-system

**Descripción**: Módulo de autenticación: register, login, JWT (30min), refresh token (7 días con rotación), logout. Rate limiting en login (5 intentos/15min). Hash bcrypt.

**Historias de usuario**: US-001, US-002, US-003, US-004, US-073

**Dependencias**: setup-infrastructure

**Requiere**: Backend configurado con security.py y BD con seed de Roles

---

### change: rbac-system

**Descripción**: Sistema de control de acceso basado en roles: 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT), dependencia require_role(roles), protección de rutas por rol, guards de navegación.

**Historias de usuario**: US-005, US-006

**Dependencias**: auth-system (necesita usuarios con roles en BD)

---

### change: categorias-data

**Descripción**: CRUD completo de categorías con jerarquía (padre_id autoreferencial), CTE recursivo para tree, validación de ciclos.

**Historias de usuario**: US-007, US-008, US-009, US-010

**Dependencias**: setup-infrastructure

---

### change: ingredientes-data

**Descripción**: CRUD de ingredientes con flag es_alergeno, soft delete.

**Historias de usuario**: US-011, US-012, US-013, US-014

**Dependencias**: setup-infrastructure

---

### change: productos-data

**Descripción**: CRUD completo de productos, M2M con categorías, M2M con ingredientes, filtrado público (disponible=true, eliminado IS NULL), búsqueda, paginación.

**Historias de usuario**: US-015, US-016, US-017, US-018, US-019, US-020, US-021, US-022, US-023

**Dependencias**: categorias-data, ingredientes-data

---

### change: direcciones-data

**Descripción**: CRUD de direcciones de entrega por cliente, predeterminada, ownership validation.

**Historias de usuario**: US-024, US-025, US-026, US-027, US-028

**Dependencias**: auth-system

---

### change: pedidos-data

**Descripción**: Creación de pedidos con Unit of Work atómico, snapshots (precio, dirección), validación stock, máquina de estados (PENDIENTE → CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO → ENTREGADO/CANCELADO), historial de estados append-only.

**Historias de usuario**: US-035, US-036, US-037, US-038, US-039, US-040, US-041, US-042, US-043, US-044, US-049, US-050, US-051

**Dependencias**: productos-data, direcciones-data

---

### change: pagos-mercadopago

**Descripción**: Integración con MercadoPago Checkout API, creación de preferencia, webhook IPN, transición automática PENDIENTE→CONFIRMADO al aprobar pago, idempotency key, restauración de stock al cancelar pedido confirmado.

**Historias de usuario**: US-045, US-046, US-047, US-048

**Dependencias**: auth-system, pedidos-data

---

### change: frontend-auth

**Descripción**: UI de autenticación: formulario login, registro, logout. AuthStore con persistencia. Interceptor Axios para 401 → refresh automático.

**Historias de usuario**: US-066, US-067, US-075, US-076

**Dependencias**: setup-frontend, auth-system

---

### change: frontend-catalog

**Descripción**: Catálogo público: listado de productos con filtros (categoría, búsqueda, precio), paginación, detalle de producto con ingredientes y alérgenos.

**Historias de usuario**: US-018, US-019, US-023

**Dependencias**: setup-frontend, productos-data

---

### change: frontend-cart

**Descripción**: Carrito de compras en Zustand con persistencia (localStorage), agregar/quitar items, personalización de ingredientes, actualización de cantidad.

**Historias de usuario**: US-029, US-030, US-031, US-032, US-033, US-034

**Dependencias**: setup-frontend

---

### change: frontend-checkout

**Descripción**: Checkout flow: selección de dirección, forma de pago, integración MercadoPago.js, redirect a pago, retorno.

**Historias de usuario**: US-035, US-045

**Dependencias**: frontend-cart, frontend-auth, pedidos-data, pagos-mercadopago

---

### change: frontend-admin

**Descripción**: Panel de administración: navegación por rol, gestión de pedidos (avanzar/cancelar estados), lista de pedidos, métricas básicas (ventas por día, productos más vendidos).

**Historias de usuario**: US-051, US-052, US-053, US-054, US-055

**Dependencias**: setup-frontend, rbac-system, pedidos-data

---

## Orden de Implementación

```
FASE 1: FUNDACIÓN
├── setup-infrastructure
└── setup-frontend

FASE 2: BACKEND CORE
├── auth-system
├── rbac-system
├── categorias-data
├── ingredientes-data
├── productos-data
├── direcciones-data
├── pedidos-data
└── pagos-mercadopago

FASE 3: FRONTEND
├── frontend-auth
├── frontend-catalog
├── frontend-cart
├── frontend-checkout
└── frontend-admin
```

---

## Diagrama de Dependencias

```
                    setup-infrastructure
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        setup-frontend             auth-system
              │                         │
              ├── frontend-auth ◄───────┤
              │                         │
              ├── frontend-cart         │
              │                         │
              ├── frontend-catalog ◄────┼──► productos-data
              │                         │         │
              │                         │         ▼
              │                         │  categorias-data
              │                         │         │
              │                         │         ▼
              │                         │  ingredientes-data
              │                         │
              │                    rbac-system
              │                         │
              ├── frontend-admin ◄──────┼──► pedidos-data
              │                         │         │
              │                         │         ▼
              │                         │  direcciones-data
              │                         │         │
              │                         │         ▼
              │                         └──► pagos-mercadopago
              │                                   │
              ▼                                   │
        frontend-checkout ◄─────────────────────┘
```

---

## Resumen

| Fase | Changes | Total |
|------|---------|-------|
| Fundación | setup-infrastructure, setup-frontend | 2 |
| Backend Core | auth-system, rbac-system, categorias-data, ingredientes-data, productos-data, direcciones-data, pedidos-data, pagos-mercadopago | 8 |
| Frontend | frontend-auth, frontend-catalog, frontend-cart, frontend-checkout, frontend-admin | 5 |
| **TOTAL** | | **15** |

Cada change genera: `proposal.md`, `design.md`, `tasks.md`. Total: 45 artefactos.
