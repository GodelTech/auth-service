import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from src.data_access.postgresql.errors import TokenIncorrectError
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)


async def incorrect_token_error_handler(
    _: Request, exc: TokenIncorrectError
) -> JSONResponse:
    logger.exception(exc)

    content = {"detail": "Incorrect Token"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
