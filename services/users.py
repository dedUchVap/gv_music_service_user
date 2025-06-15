import datetime
import hashlib
import secrets
from datetime import timedelta
from sqlalchemy.orm import selectinload

import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from crud.user import UserCrud
from models.user import UserModel
from scheme.user import User, UserRegister, UserLogin
from crud.user import user_cruds

class UserServices:

    @classmethod
    def hash_password(cls,password: str) -> str:
        solt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), solt)
        return hashed.decode('utf-8')

    @classmethod
    def verify_password(cls,password_hashed: str,password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hashed.encode('utf-8')
        )

    @classmethod
    def get_valid_bd_user(cls, data: UserRegister) -> User:
        password_hashed = cls.hash_password(data.password)
        user = User(password=password_hashed, username=data.username, token_author=data.token_author)
        return user

    @classmethod
    async def auth_user(cls, data: UserLogin, session: AsyncSession) -> UserModel | None:
        user = await user_cruds.get_by_value(db=session, username=data.username, options=[selectinload(UserModel.role)])
        if user:
            if cls.verify_password(user.password_hashed, data.password):
                return user
        return None


def create_token(sub: int, role: int, expires_delta: timedelta | None = None) -> str:
    now_time = datetime.datetime.now()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = expires_delta + now_time

    payload = {
        "sub": str(sub),
        "role": str(role),
        "iat": now_time,
        "expire": int(expire.timestamp())
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(expires_at: datetime.datetime = None) -> tuple[str, str, datetime.datetime]:
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if expires_at is None:
        expires_at = datetime.datetime.now() + timedelta(days=15)
    return token, token_hash, expires_at
