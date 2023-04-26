from typing import Union
from src.business_logic.get_tokens.errors import (
    InvalidGrantError,
    InvalidRedirectUriError,
)
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


ExceptionsToHandle = Union[InvalidGrantError, InvalidRedirectUriError]


async def http400_invalid_grant_handler(
    _: Request, exc: ExceptionsToHandle
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "invalid_grant"}
    return JSONResponse(
        content=content, headers=headers, status_code=HTTP_400_BAD_REQUEST
    )
