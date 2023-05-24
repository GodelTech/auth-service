import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.data_access.postgresql.errors import GrantNotFoundError

logger = logging.getLogger(__name__)


async def grant_not_found_error_handler(
    _: Request, exc: GrantNotFoundError
) -> JSONResponse:
    logger.exception(exc)

    content = {"detail": "Incorrect Token"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
