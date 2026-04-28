# agents.md — Food Store

## Propósito del agente

Este agente debe asistir en el desarrollo de **Food Store**, un e-commerce de alimentos con frontend en **React + TypeScript + Vite** y backend en **FastAPI + SQLModel + PostgreSQL**. Su objetivo es producir cambios coherentes con la especificación del proyecto, sin romper la arquitectura, las reglas de negocio ni la trazabilidad definida en el sistema. fileciteturn0file0 fileciteturn0file2

## Contexto del proyecto

Food Store contempla cinco actores: Cliente, Admin, Gestor de Stock, Gestor de Pedidos y Sistema. El dominio incluye autenticación con JWT y refresh tokens, catálogo de productos, carrito, direcciones, pedidos con máquina de estados, pagos con MercadoPago y panel administrativo. fileciteturn0file0

## Stack y decisiones base

Backend:
- FastAPI
- SQLModel
- PostgreSQL
- Alembic
- Passlib con bcrypt
- python-jose o PyJWT
- slowapi
- SDK oficial de MercadoPago para Python

Frontend:
- React
- TypeScript
- Vite
- TanStack Query
- TanStack Form
- Zustand
- Axios
- Tailwind CSS
- recharts
- SDK de MercadoPago para navegador

Estas tecnologías forman parte explícita de la especificación del sistema y deben respetarse al crear o modificar código. fileciteturn0file0 fileciteturn0file2

## Principios de trabajo del agente

1. Mantener siempre la separación entre frontend y backend.
2. No inventar entidades, endpoints ni reglas que no estén en la especificación.
3. Priorizar consistencia con el modelo de datos, las historias de usuario y las reglas de negocio.
4. Evitar cambios “rápidos” que rompan trazabilidad, snapshots, soft delete o control de permisos.
5. Respetar la arquitectura por capas y la organización por features.
6. Cuando exista ambigüedad entre documentos, preferir la especificación más reciente y el comportamiento descrito en las historias de usuario.

## Arquitectura obligatoria del backend

El backend sigue un flujo unidireccional:

**Router → Service → Unit of Work → Repository → Model**

Reglas:
- El Router solo recibe requests, valida entrada y delega.
- El Service concentra la lógica de negocio.
- El Unit of Work controla transacciones, commit y rollback.
- El Repository accede a datos.
- El Model define las tablas y relaciones.

Ninguna capa debe importar a una superior. El agente no debe mezclar lógica de negocio en routers ni acceso a datos en services. fileciteturn0file0 fileciteturn0file2

## Organización del backend

El proyecto usa un enfoque **feature-first**. Cada módulo debe contener sus piezas funcionales juntas. Módulos principales:
- auth
- refreshtokens
- usuarios
- direcciones
- categorias
- productos
- pedidos
- pagos
- admin

Cada módulo suele incluir:
- `model.py`
- `schemas.py`
- `repository.py`
- `service.py`
- `router.py`

El agente debe seguir esta estructura al crear nuevos módulos o extender los existentes. fileciteturn0file0

## Organización del frontend

El frontend sigue **Feature-Sliced Design** con capas:
- `app`
- `pages`
- `widgets`
- `features`
- `entities`
- `shared`

Regla de imports:
- una capa solo importa desde capas inferiores;
- `shared` contiene lo reutilizable;
- `entities` modela dominio;
- `features` encapsula acciones de usuario;
- `widgets` compone bloques;
- `pages` arma vistas;
- `app` configura providers, routing y estilos globales.

El agente no debe mezclar responsabilidades entre capas. fileciteturn0file0

## Estado del cliente vs estado del servidor

Usar esta separación siempre:

**Zustand**
- carrito
- autenticación
- estado de checkout
- UI local
- preferencias visuales

**TanStack Query**
- productos
- pedidos
- usuarios
- categorías
- datos que vienen del backend

No duplicar en Zustand lo que ya es estado del servidor. No almacenar en TanStack Query lo que pertenece al cliente. fileciteturn0file0 fileciteturn0file2

## Reglas de negocio críticas

### Autenticación y seguridad
- La contraseña nunca se guarda en texto plano; se hashea con bcrypt.
- El login usa JWT access token y refresh token.
- El rol CLIENT se asigna automáticamente al registrarse.
- El rate limiting del login debe proteger contra fuerza bruta.
- El sistema no debe filtrar si un login falló por email inexistente o contraseña incorrecta.
- Los datos sensibles de tarjeta no pasan por el backend. fileciteturn0file1 fileciteturn0file0

### RBAC
- Existen cuatro roles fijos: ADMIN, STOCK, PEDIDOS y CLIENT.
- Un usuario puede tener múltiples roles.
- Solo ADMIN puede asignar roles.
- CLIENT solo accede a sus propios datos.
- STOCK no accede a pedidos ni usuarios.
- PEDIDOS no accede a catálogo ni gestión de usuarios. fileciteturn0file1

### Catálogo
- Categorías jerárquicas con `padre_id`.
- No permitir ciclos en la jerarquía.
- Producto con precio numérico fijo, stock entero no negativo y flag `disponible`.
- Ingredientes con flag `es_alergeno`.
- Relación M2M entre productos-categorías y productos-ingredientes.
- Soft delete con timestamp lógico; no borrar físicamente salvo excepción explícita de infraestructura. fileciteturn0file0 fileciteturn0file1

### Carrito
- El carrito vive solo en el cliente.
- Debe persistir en localStorage.
- Si un producto se agrega dos veces, se incrementa cantidad.
- La personalización solo puede usar ingredientes realmente asociados al producto. fileciteturn0file1

### Pedidos
- Crear pedido de forma atómica.
- Usar snapshots de precio y dirección.
- Validar stock dentro de la transacción.
- No dejar estados intermedios persistidos si algo falla.
- Registrar cada transición en historial append-only.
- Respetar la máquina de estados: PENDIENTE → CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO → ENTREGADO, con CANCELADO como estado terminal alternativo. fileciteturn0file0 fileciteturn0file1

### Pagos
- Integrar MercadoPago según la arquitectura del proyecto.
- Usar `external_reference` para vincular pago y pedido.
- Hacer el procesamiento idempotente.
- Tratar los webhooks como eventos que deben verificarse contra la API real antes de confirmar cambios de estado. fileciteturn0file0 fileciteturn0file1

## Convenciones de datos

- Usar campos de auditoría en las tablas principales.
- Mantener `creado_en` y `actualizado_en`.
- Aplicar soft delete con campo de eliminación lógica.
- Preservar registros históricos mediante snapshots.
- Mantener el historial de estados como append-only.
- Respetar IDs estables en seeds para roles y estados de pedido.
- El seed debe ser idempotente. fileciteturn0file0 fileciteturn0file1

## Estilo de implementación

- Escribir código tipado y explícito.
- Preferir funciones pequeñas y con responsabilidad única.
- Validar inputs en la capa de entrada.
- No mezclar queries con lógica de negocio.
- Usar transacciones para operaciones compuestas.
- Evitar acoplamiento entre módulos.
- No introducir dependencias innecesarias.

## Qué debe hacer el agente ante una tarea

1. Identificar el módulo afectado.
2. Verificar la capa correcta.
3. Aplicar la regla de negocio correspondiente.
4. Mantener la estructura existente.
5. Si una decisión puede romper contratos de datos o permisos, detenerse y pedir confirmación.

## Qué no debe hacer el agente

- No inventar endpoints.
- No cambiar nombres de roles, estados o tablas sin motivo fuerte.
- No eliminar soft delete ni historial.
- No guardar datos sensibles donde no corresponde.
- No mezclar cliente y servidor.
- No romper el flujo Router → Service → UoW → Repository → Model.
- No romper la organización feature-first / FSD.

## Prioridad de referencia

Cuando haya diferencias entre documentos, usar este orden de referencia:
1. Especificación técnica v5 del proyecto.
2. Historias de usuario y reglas de negocio.
3. Implementación existente en el repositorio.
4. Buenas prácticas generales, siempre que no contradigan lo anterior.

## Resultado esperado

Todo cambio producido por este agente debe:
- encajar en la arquitectura del proyecto,
- respetar las reglas de negocio,
- ser mantenible,
- ser coherente con el modelo de datos,
- y poder escalar sin reescrituras grandes.
