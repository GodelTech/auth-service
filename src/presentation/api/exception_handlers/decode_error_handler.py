import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from jwt.exceptions import DecodeError
from starlette.status import HTTP_404_NOT_FOUND

logger = logging.getLogger(__name__)


async def decode_error_handler(_: Request, exc: DecodeError) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Bad id_token_hint"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
