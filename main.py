import colorama
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from routs.user_route import router as router_user
from routs.auth_route import router as router_auth

origins = [
    'http://127.0.0.2:8000',
    'http://localhost:8000',
    'http://localhost',
]

colorama.init()
app = FastAPI(
    version='1.0.0',
    title='Auth Service',
    description='Microservice for authentication')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
app.include_router(router_user)
app.include_router(router_auth)

if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.2', reload=True)
