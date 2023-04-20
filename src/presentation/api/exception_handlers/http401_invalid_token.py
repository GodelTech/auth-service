from src.business_logic.common.errors import InvalidAuthorizationTokenError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED


async def http401_invalid_token_handler(
    _: Request, exc: InvalidAuthorizationTokenError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {
        "error": "invalid_token",
        "error_description": "Incorrect authorization token",
    }
    return JSONResponse(
        content=content, headers=headers, status_code=HTTP_401_UNAUTHORIZED
    )
