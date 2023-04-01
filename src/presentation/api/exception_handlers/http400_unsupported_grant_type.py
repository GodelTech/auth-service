from src.business_logic.get_tokens.errors import UnsupportedGrantTypeError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


async def http400_unsupported_grant_type_handler(_: Request, exc: UnsupportedGrantTypeError) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "unsupported_grant_type"}
    return JSONResponse(
        content=content,
        headers=headers,
        status_code=HTTP_400_BAD_REQUEST
    )
