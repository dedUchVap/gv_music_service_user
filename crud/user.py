import datetime

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.crud_base import CRUDBase
from models.user import UserModel, RefreshTokensModel
from scheme.user import User


class UserCrud(CRUDBase[UserModel, User, User]):

    @classmethod
    async def add_user(cls, data:User,session: AsyncSession) -> UserModel:
        if data.token_author == 'super_secret':
            role = 1
        else:
            role = 2
        user = UserModel(
            username=data.username,
            author_token=data.token_author,
            password_hashed=data.password,
            role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_user_by_name(cls,username: str,session: AsyncSession) -> (UserModel | None):
        stmt = select(UserModel).filter_by(username=username)
        result = await session.execute(stmt)

        return result.scalars().first()

    @staticmethod
    async def get_refresh_token(token_hash: str,session: AsyncSession,revoked: bool = False) -> RefreshTokensModel | None:
        stmt = select(RefreshTokensModel).filter_by(token_hash=token_hash, revoked=revoked)
        result = await session.execute(stmt)
        result = result.scalar_one_or_none()
        return result

    @staticmethod
    async def save_refresh_token(token_hash: str, user_id: int, session: AsyncSession, expires_at: datetime.datetime = None):
        if expires_at is None:
            expires_at = timedelta(days=15) + datetime.datetime.now()
        token = RefreshTokensModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        session.add(token)
        await session.commit()

user_cruds = UserCrud(UserModel)
