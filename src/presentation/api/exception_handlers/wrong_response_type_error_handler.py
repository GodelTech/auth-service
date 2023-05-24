import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from src.data_access.postgresql.errors import WrongResponseTypeError

logger = logging.getLogger(__name__)


async def wrong_response_type_error_handler(
    _: Request, exc: WrongResponseTypeError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Bad response type"}

    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content=content,
    )
