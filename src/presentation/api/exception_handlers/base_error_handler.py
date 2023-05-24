import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


async def base_bad_request_error_handler(
    _: Request, exc: BaseException
) -> JSONResponse:
    logger.exception(exc)

    content = {"details": exc.args}

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content,
    )


async def base_not_found_error_handler(
    _: Request, exc: BaseException
) -> JSONResponse:
    logger.exception(exc)

    content = {"details": "Instance not found"}

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=content,
    )
