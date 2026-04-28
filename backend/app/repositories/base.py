"""Generic BaseRepository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository with common CRUD operations.
    
    Type Parameters:
        ModelType: The SQLModel class this repository manages
    
    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(db, User)
    """
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        """Initialize repository.
        
        Args:
            db: AsyncSession from get_db dependency
            model: The SQLModel class this repository manages
        """
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get an entity by its primary key.
        
        Args:
            id: The primary key value
            
        Returns:
            The entity if found, None otherwise
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get all entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of entities
        """
        result = await self.db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count total entities.
        
        Returns:
            Total count
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create a new entity.
        
        Args:
            obj: The entity to create
            
        Returns:
            The created entity with generated ID
        """
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing entity.
        
        Args:
            obj: The entity with updated values
            
        Returns:
            The updated entity
        """
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, obj: ModelType) -> None:
        """Delete an entity.
        
        Args:
            obj: The entity to delete
        """
        await self.db.delete(obj)
        await self.db.flush()