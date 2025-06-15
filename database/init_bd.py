from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase

from typing import AsyncGenerator


DATABASE_URL = 'postgresql+asyncpg://pirat:123@localhost/gvmus'
engine = create_async_engine(DATABASE_URL, echo=True)

class Base(DeclarativeBase):
    pass

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


