from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from common.constants import SECRET_KEY, ALGORITHM
from scheme.user import User
from crud.user import UserCrud, user_cruds
from execption.custom_error import credentials_error
from routs.auth_route import scheme_oauth

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.init_bd import get_session
from models.user import UserModel
from jose import jwt

router = APIRouter(prefix='/users', tags=['auth_route'])


async def get_current_user(token: Annotated[str, Depends(scheme_oauth)],
                           session: AsyncSession = Depends(get_session)) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('sub')
    if user_id is None:
        raise credentials_error
    user = await user_cruds.get(session, int(user_id), options=([selectinload(UserModel.role_name)]))
    user = User(username=user.username, password='', role=str(user.role_name.role_name), token_author='')
    return user.model_dump()


@router.get('/get_me')
async def get_me(user_id: Annotated[int, Depends(get_current_user)]):
    return JSONResponse(user_id)
