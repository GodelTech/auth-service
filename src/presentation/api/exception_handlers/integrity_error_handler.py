from sqlalchemy import exc
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from starlette import status 

logger = logging.getLogger(__name__)


async def integryty_error_handler(_: Request, exc: exc.IntegrityError) -> JSONResponse:
    logger.exception(exc.args)
    details = exc.args[0]
    index = details.find("DETAIL:  ")
    if index != -1:
        details = details[index + len("DETAIL:  "):]
    else:
        details = details
    return JSONResponse(
        status_code = getattr(exc, 'status_code', None) or status.HTTP_409_CONFLICT,
        content={"message": "Error in data"} | {'details': details},
    )