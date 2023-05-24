import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)

logger = logging.getLogger(__name__)


async def persistent_grant_not_found_error_handler(
    _: Request, exc: PersistentGrantNotFoundError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "You are not logged in"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
