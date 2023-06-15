from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.get_tokens.errors import InvalidPkceCodeError


async def http400_invalid_pkce_handler(
        _: Request, 
        exc: InvalidPkceCodeError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "invalid_request", "error_description": "code challenge required."}
    return JSONResponse(
        content=content,
        headers=headers,
        status_code=HTTP_400_BAD_REQUEST
    )
