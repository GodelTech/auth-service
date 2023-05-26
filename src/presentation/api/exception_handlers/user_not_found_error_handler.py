import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND
from src.data_access.postgresql.errors import UserNotFoundError

logger = logging.getLogger(__name__)


async def user_not_found_error_handler(
    _: Request, exc: UserNotFoundError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "User not found"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
