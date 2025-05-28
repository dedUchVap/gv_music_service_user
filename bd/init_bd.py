from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = 'postgresql+asyncpg://postgres:123@localhost/gvMus'
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Base: DeclarativeBase


