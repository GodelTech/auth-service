import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from src.data_access.postgresql.errors import ClaimsNotFoundError

logger = logging.getLogger(__name__)


async def claims_not_found_error_handler(
    _: Request, exc: ClaimsNotFoundError
) -> JSONResponse:
    logger.exception(exc)

    content = {"detail": "You don't have permission for this claims"}

    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content=content,
    )
