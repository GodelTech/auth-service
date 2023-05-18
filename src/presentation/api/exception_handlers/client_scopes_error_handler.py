import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from src.data_access.postgresql.errors import ClientScopesError

logger = logging.getLogger(__name__)


async def client_scopes_error_handler(_: Request, exc: ClientScopesError) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Invalid scope"}

    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
