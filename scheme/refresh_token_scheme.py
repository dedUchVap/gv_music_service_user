from pydantic import BaseModel

class TokenUpdate(BaseModel):
    revoked: bool = False

class TokenCreate(BaseModel):
    token_hash: str
    