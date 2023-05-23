import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.data_access.postgresql.errors import TokenIncorrectError
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)


async def base_error_handler(_: Request, exc: BaseException) -> JSONResponse:
    logger.exception(exc)

    content = {"details": exc.args}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )