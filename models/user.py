from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from bd.init_bd import Base, engine
import asyncio

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hashed = Column(String, unique=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    author_token = Column(String, nullable=True)


