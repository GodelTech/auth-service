import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from src.data_access.postgresql.errors import ThirdPartyStateDuplicationError

logger = logging.getLogger(__name__)


async def third_party_state_duplication_error_handler(
    _: Request, exc: ThirdPartyStateDuplicationError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Third Party State already exists"}

    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content=content,
    )
