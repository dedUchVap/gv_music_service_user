from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix='/users', tags=['auth_route'])

scheme_oauth = OAuth2PasswordBearer(tokenUrl='/auth/token')
