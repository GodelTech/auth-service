from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthInvalidStateError,
)


async def http400_third_party_auth_invalid_request_data_handler(
    _: Request, exc: ThirdPartyAuthInvalidStateError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": exc.args[-1]}
    return JSONResponse(
        content=content, headers=headers, status_code=HTTP_400_BAD_REQUEST
    )
