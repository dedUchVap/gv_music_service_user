from pydantic import BaseModel, model_validator, Field
from typing_extensions import Self


class UserRegister(BaseModel):
    username: str = Field(max_length=60)
    token_author: str | None = None
    password: str = Field(min_length=3, max_length=64)
    password_confirm: str

    @model_validator(mode='after')
    def password_confirm_check(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError('Passwords must match')
        return self


class User(BaseModel):
    username: str
    token_author: str | None
    password: str
    role: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
