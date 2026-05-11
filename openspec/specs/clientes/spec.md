# Clientes

Specification for customer management — CRUD operations, security, and validations.

## Requirements

### Requirement: Crear, listar, modificar y borrar clientes
El sistema SHALL permitir la gestión CRUD de clientes finales con los siguientes campos requeridos: id, nombre, apellido, email (único), telefono, direccion, activo, creado_en, actualizado_en.

#### Scenario: Alta de cliente por ADMIN
- **WHEN** un usuario ADMIN envía un POST a /api/v1/clientes con datos válidos
- **THEN** el sistema crea el Cliente y responde 201 con los datos creados

#### Scenario: No-ADMIN no puede crear
- **WHEN** un usuario CLIENT, STOCK o PEDIDOS intenta POSTear
- **THEN** el sistema responde 403 Forbidden

#### Scenario: Email repetido
- **WHEN** se intenta crear/modificar un cliente con email ya registrado
- **THEN** el sistema rechaza y responde 422 con error por email duplicado

#### Scenario: Consulta paginada
- **WHEN** un usuario autenticado pide GET /api/v1/clientes?page=1&size=20
- **THEN** recibe 200 y lista paginada de clientes activos

#### Scenario: CLIENT solo accede a su cliente
- **WHEN** CLIENT autenticado hace GET /api/v1/clientes/{id}
- **THEN** sólo puede acceder a su propio cliente (por email vinculado); acceso a otros da 403

#### Scenario: Modificar cliente
- **WHEN** un ADMIN envía PUT /api/v1/clientes/{id} con datos válidos
- **THEN** el sistema actualiza y responde 200 con los datos modificados

#### Scenario: Baja de cliente (soft-delete)
- **WHEN** un ADMIN ejecuta DELETE /api/v1/clientes/{id}
- **THEN** el cliente pasa a activo=False, responde 204 e invisible en GET/lista
