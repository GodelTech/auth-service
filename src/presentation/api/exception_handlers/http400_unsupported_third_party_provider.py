from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.third_party_auth.errors import (
    UnsupportedThirdPartyAuthProviderError,
)


async def http400_unsupported_third_party_auth_provider_handler(
    _: Request, exc: UnsupportedThirdPartyAuthProviderError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "unsupported_auth_provider"}
    return JSONResponse(
        content=content, headers=headers, status_code=HTTP_400_BAD_REQUEST
    )
