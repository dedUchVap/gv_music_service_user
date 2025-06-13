from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from common.helpers import translate_error


class ValidationErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except RequestValidationError as e:
            errors = []

            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'] if loc != 'body')
                custom_msg = translate_error(error)
                errors.append({"field": field, "message": custom_msg})

            return JSONResponse(status_code=422, content={"errors": errors})