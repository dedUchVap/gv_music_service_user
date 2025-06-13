from fastapi.exceptions import HTTPException
credentials_error = HTTPException(
    status_code=401,
    detail='Failed to verify account details',
    headers={"WWW-Authenticate": "Bearer"})