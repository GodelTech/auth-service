from src.business_logic.common.errors import InvalidClientIdError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


async def http400_invalid_client_handler(
        _: Request, 
        exc: InvalidClientIdError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "invalid_client"}
    return JSONResponse(
        content=content,
        headers=headers,
        status_code=HTTP_400_BAD_REQUEST
    )
