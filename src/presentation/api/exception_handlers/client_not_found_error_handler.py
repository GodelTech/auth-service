import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.data_access.postgresql.errors import ClientNotFoundError

logger = logging.getLogger(__name__)


async def client_not_found_error_handler(_: Request, exc: ClientNotFoundError) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Client not found"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
