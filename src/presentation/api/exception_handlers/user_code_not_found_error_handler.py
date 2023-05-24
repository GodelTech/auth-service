import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.data_access.postgresql.errors import UserCodeNotFoundError

logger = logging.getLogger(__name__)


async def user_code_not_found_error_handler(_: Request, exc: UserCodeNotFoundError) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Wrong user code"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
