import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthInvalidStateError,
)

logger = logging.getLogger(__name__)


async def invalid_state_error_handler(
    _: Request, exc: ThirdPartyAuthInvalidStateError
) -> JSONResponse:
    logger.exception(exc)

    content = {"error": "invalid_state"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
