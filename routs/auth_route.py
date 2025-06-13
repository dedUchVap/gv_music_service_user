import datetime
import hashlib
from typing import Annotated

from fastapi import Form, Depends, APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import UserCrud, user_cruds
from database.init_bd import get_session
from scheme.user import UserRegister, Token
from services.users import UserServices, create_token, create_refresh_token

scheme_oauth = OAuth2PasswordBearer(tokenUrl='/auth/token')
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
        token_access = create_token(sub=user_in_db.id, role=user_in_db.role)
        token_refresh, token_hash = create_refresh_token()
        await user_cruds.save_refresh_token(token_hash, user_in_db.id, session=session)
        result = JSONResponse(content={'access_token': token_access, 'token_type': 'bearer'})
        result.set_cookie('refresh_token', value=token_refresh, httponly=True)
        return result
    return HTTPException(detail='Пользователь не найден', status_code=404)


@router.post('/refresh')
async def refresh_token(request: Request, session: Annotated[AsyncSession, Depends(get_session)]):
    token_refresh = request.cookies.get('refresh_token')
    if token_refresh is None:
        raise HTTPException(status_code=401, detail='No refresh token')

    token_hash = hashlib.sha256(token_refresh.encode()).hexdigest()

    token_hash_in_db = await user_cruds.get_by_value(session, token_hash=token_hash)
    if token_hash_in_db is None:
        raise HTTPException(status_code=401, detail='Invalid token')

    if token_hash_in_db.expires_at < datetime.datetime.now():
        raise HTTPException(status_code=401, detail='Invalid token')

    user_id = token_hash_in_db.user_id

    access_token = create_token(user_id, role=token_hash_in_db.user.role.role_name)
    token_refresh, token_hash = create_refresh_token()
    await user_cruds.save_refresh_token(token_hash, user_id, session=session)
    response = JSONResponse({'access_token': access_token, 'token_type': 'bearer'})
    response.set_cookie(key='refresh_token', value=token_refresh)
    return response