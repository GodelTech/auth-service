import logging
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status
from src.data_access.postgresql.errors.auth_token import IncorrectAuthTokenError

logger = logging.getLogger(__name__)


async def incorrect_token_auth_error_handler(_: Request, exc: IncorrectAuthTokenError) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        status_code = getattr(exc, 'status_code', None) or status.HTTP_401_UNAUTHORIZED,
        content= exc.message | {'details': exc.args},
    )


auth_token_error_mapping ={
    IncorrectAuthTokenError : incorrect_token_auth_error_handler 
    }