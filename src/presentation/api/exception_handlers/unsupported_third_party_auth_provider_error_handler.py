import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.third_party_auth.errors import (
    UnsupportedThirdPartyAuthProviderError,
)

logger = logging.getLogger(__name__)


async def unsupported_third_party_auth_provider_error_handler(
    _: Request, exc: UnsupportedThirdPartyAuthProviderError
) -> JSONResponse:
    logger.exception(exc)

    content = {"error": "unsupported_auth_provider"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
