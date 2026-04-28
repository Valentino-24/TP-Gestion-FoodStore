---
name: sqlmodel-database
description: |
  Design and implement database schemas using SQLModel with sync and async patterns. Use this skill when creating database models, setting up PostgreSQL connections, defining relationships (one-to-many, many-to-many), implementing FastAPI dependency injection, or migrating schemas.
---

# SQLModel Database

**Dependencies**: SQLModel, SQLAlchemy 2.0, asyncpg (PostgreSQL)

---

## Quick Start

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
```

---

## Database Connection

### Sync (Development)
```python
from sqlmodel import create_engine

DATABASE_URL = "postgresql://user:pass@localhost/foodstore"
engine = create_engine(DATABASE_URL, echo=True)
```

### Async (Recommended for Production)
```python
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/foodstore"
async_engine = create_async_engine(DATABASE_URL, echo=True)

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

---

## Relationships

### One-to-Many
```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    
    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    
    team: Team | None = Relationship(back_populates="heroes")
```

### Many-to-Many
```python
# Requires association table
class HeroTeam(SQLModel, table=True):
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
```

---

## FastAPI Dependency Injection

```python
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

DBSession = AsyncSession = Depends(get_db)
```

---

## CRUD Operations

```python
from sqlmodel import select

# Create
user = User(email="test@example.com", hashed_password="hash")
session.add(user)
session.commit()
session.refresh(user)

# Read
statement = select(User).where(User.email == "test@example.com")
result = session.exec(statement)
user = result.one_or_none()

# Update
user.is_active = False
session.add(user)
session.commit()

# Delete
session.delete(user)
session.commit()
```

---

## Migration with Alembic

```bash
# Generate migration
alembic revision --autogenerate -m "add users table"

# Apply migrations
alembic upgrade head
```

---

## Critical Rules

✅ Use `sqlmodel` not separate `sqlalchemy` + `pydantic`
✅ Use `asyncpg` for async PostgreSQL
✅ Define `__tablename__` explicitly for control
✅ Use `Field` for column configuration
✅ Use relationships for foreign keys
✅ Use Alembic for migrations

---

## Resources

- **SQLModel**: https://sqlmodel.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/
- **asyncpg**: https://github.com/MagicStack/asyncpg