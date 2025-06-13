from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.init_bd import Base, engine


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), nullable=False)
    password_hashed: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    author_token: Mapped[str] = mapped_column(String(), nullable=True)
    role: Mapped[int] = mapped_column(ForeignKey('role.id'))

    tokens = relationship('RefreshTokensModel', back_populates='user', cascade="all, delete-orphan")
    role_name = relationship('RoleModel', back_populates='users')


class RoleModel(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    role_name = Column(String(64), nullable=False)

    users = relationship('UserModel', back_populates='role_name')


class RefreshTokensModel(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    token_hash: Mapped[str] = mapped_column(String(256))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship('UserModel', back_populates='tokens')

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
