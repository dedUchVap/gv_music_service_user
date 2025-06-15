from datetime import datetime

from pydantic import BaseModel

class TokenUpdate(BaseModel):
    revoked: bool = False

class TokenCreate(BaseModel):
    token_hash: str
    user_id: int
    expires_at: datetime