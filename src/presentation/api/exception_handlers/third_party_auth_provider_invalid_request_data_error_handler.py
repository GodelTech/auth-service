import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthProviderInvalidRequestDataError,
)

logger = logging.getLogger(__name__)


async def invalid_request_data_error_handler(
    _: Request, exc: ThirdPartyAuthProviderInvalidRequestDataError
) -> JSONResponse:
    logger.exception(exc)

    content = {"error": "invalid_request_data"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
