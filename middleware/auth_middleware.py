from typing import Annotated

from fastapi import Depends
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.constants import SECRET_KEY, ALGORITHM
from crud.user import user_cruds
from database.init_bd import get_session
from execption.custom_error import credentials_error
from models.user import UserModel
from routs.user_route import scheme_oauth
from scheme.user import User


async def get_current_user(token: Annotated[str, Depends(scheme_oauth)],
                           session: AsyncSession = Depends(get_session)) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('sub')
    if user_id is None:
        raise credentials_error
    user = await user_cruds.get(session, int(user_id), options=([selectinload(UserModel.role)]))
    user = User(username=user.username, password='', role=str(user.role.role_name), token_author='')
    return user.model_dump()


async def get_user_info_from_token(token: Annotated[str, Depends(scheme_oauth)]) -> tuple[str, str]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('sub')
    role = payload.get('role')
    if user_id is None:
        raise credentials_error
    return user_id, role

async def require_role(require_role: str):
    def role_checker(user: Annotated[dict, Depends(get_current_user)]):
        if not user.get('role') is require_role:
            raise credentials_error
        return user
    return role_checker