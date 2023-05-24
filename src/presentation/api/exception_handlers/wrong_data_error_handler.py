import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.data_access.postgresql.errors import WrongDataError

logger = logging.getLogger(__name__)


async def wrong_data_error_handler(_: Request, exc: WrongDataError) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Wrong data has been passed"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
