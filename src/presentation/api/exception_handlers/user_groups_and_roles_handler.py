import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status
from src.data_access.postgresql.errors import UserNotInGroupError

logger = logging.getLogger(__name__)


async def user_not_in_group_error_handler(
    _: Request, exc: UserNotInGroupError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": f"For this action you need to be in group '{exc.args}'"}

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content,
    )