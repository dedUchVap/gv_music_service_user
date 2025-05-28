from passlib.context import CryptContext
from typing_extensions import deprecated

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserServices:

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password_hashed: str, password: str) -> bool:
        return pwd_context.verify(password, password_hashed)

    @classmethod
    def get_valid_bd_user(cls):
