import datetime
import hashlib
from typing import Annotated

from fastapi import Form, Depends, APIRouter, Request, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.user import UserCrud, user_cruds, refresh_tokens_cruds
from database.init_bd import get_session
from middleware.auth_middleware import get_current_user
from models.user import RefreshTokensModel, UserModel
from scheme.refresh_token_scheme import TokenCreate
from scheme.user import UserRegister
from services.users import UserServices, create_token, create_refresh_token

router = APIRouter(prefix='/auth')

@router.post('/register')
async def register(data: Annotated[UserRegister, Form()], session: AsyncSession = Depends(get_session)):
    user = UserServices.get_valid_bd_user(data)

    if await UserCrud.get_user_by_name(username=user.username, session=session):
        return JSONResponse('Пользователь уже имеется', status_code=409)
    await UserCrud.add_user(user, session)
    return JSONResponse('', status_code=200)


@router.post('/token')
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: AsyncSession = Depends(get_session)):
    user_in_db = await UserServices.auth_user(form_data, session)
    if user_in_db:
        token_access = create_token(sub=user_in_db.id, role=user_in_db.role.role_name)
        token_refresh, token_hash, expires_at = create_refresh_token()
        await user_cruds.save_refresh_token(token_hash, user_in_db.id, session=session)
        result = JSONResponse(content={'access_token': token_access, 'token_type': 'bearer'})
        result.set_cookie('refresh_token', value=token_refresh, httponly=True)
        return result
    raise HTTPException(detail='Пользователь не найден', status_code=404)


@router.post('/refresh')
async def refresh_token(request: Request, session: Annotated[AsyncSession, Depends(get_session)]):
    token_refresh = request.cookies.get('refresh_token')
    if token_refresh is None:
        raise HTTPException(status_code=401, detail='No refresh token')

    token_hash = hashlib.sha256(token_refresh.encode()).hexdigest()

    token_hash_in_db = await refresh_tokens_cruds.get_by_value(session, token_hash=token_hash, options=[selectinload(RefreshTokensModel.user).selectinload(UserModel.role)])
    if token_hash_in_db is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    if token_hash_in_db.expires_at < datetime.datetime.now():
        raise HTTPException(status_code=401, detail='Invalid token')

    user_id = token_hash_in_db.user_id

    access_token = create_token(user_id, role=token_hash_in_db.user.role.role_name)
    token_refresh, token_hash, expires_at = create_refresh_token()
    await refresh_tokens_cruds.create(object_in=TokenCreate(token_hash=token_hash, expires_at=expires_at, user_id=user_id), db=session)
    response = JSONResponse({'access_token': access_token, 'token_type': 'bearer'})
    response.set_cookie(key='refresh_token', value=token_refresh)
    return response


@router.get('/get_me')
async def get_me(user_data: Annotated[int, Depends(get_current_user)]):
    return JSONResponse(user_data)

@router.get('/logout')
async def logout(response: Response, request: Request, user: Annotated[dict, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
    token_ref = request.cookies.get('refresh_token')
    if token_ref:
        token_hash = hashlib.sha256(token_ref.encode()).hexdigest()
        token_from_bd = await refresh_tokens_cruds.get_by_value(db=session, token_hash=token_hash)
        if token_from_bd is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        await refresh_tokens_cruds.remove(db=session, id=token_from_bd.id)
        response.status_code = 200
        response.delete_cookie('refresh_token')
        return response
    return None