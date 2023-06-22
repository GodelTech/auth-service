from src.business_logic.common.errors import InvalidClientScopeError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Union


async def http400_invalid_scope_handler(
        _: Request, 
        exc: InvalidClientScopeError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "invalid_scope"}
    return JSONResponse(
        content=content,
        headers=headers,
        status_code=HTTP_400_BAD_REQUEST
    )
