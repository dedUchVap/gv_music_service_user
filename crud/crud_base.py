from typing import TypeVar, Generic, Type, List, Sequence

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
CreateScheme = TypeVar('CreateScheme', bound=BaseModel)


class CRUDBase(Generic[ModelType, UpdateSchema, CreateScheme]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int, options: None | Sequence = None) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id)
        if options:
            stmt = stmt.options(*options)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def remove(self, db: AsyncSession, id: int) -> ModelType | None:
        db_object = await self.get(db, id)

        if not db_object:
            return None
        await db.delete(db_object)
        await db.commit()
        return db_object

    async def get_multi(self, db: AsyncSession, offset: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, id: int, object_in: UpdateSchema) -> ModelType | None:
        result = await db.get(db, id)
        if not result:
            return None
        data = object_in.model_dump(exclude=True)
        for key, value in data.items():
            setattr(result, key, value)

        await db.commit()
        await db.refresh(result)
        return result

    async def create(self, db: AsyncSession, object_in: CreateScheme) -> ModelType:
        db_object = self.model(**object_in.model_dump())
        db.add(db_object)
        await db.commit()
        await db.refresh(db_object)
        return db_object

    async def get_by_value(self, db: AsyncSession, one_result: bool = True, **kwargs):
        stmt = select(self.model).filter_by(**kwargs)
        result = await db.execute(stmt)
        if one_result:
            return result.one_or_none()
        return result.scalars().all()
