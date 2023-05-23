import logging
from typing import Any
from fastapi import Request
from src.data_access.postgresql.errors.auth_token import NoAuthTokenError, IncorrectAuthTokenError, RevokedAuthTokenError
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository


logger = logging.getLogger(__name__)

async def authorization_middleware(request: Request) -> Any:
    jwt_service = JWTService()
    token = request.headers.get("authorization") or request.headers.get("auth-swagger")
    if token is None:
        logger.exception("Authorization Failed (No authorization or auth-swagger in Request)")
        raise NoAuthTokenError

    session = request.state.session
    blacklisted_repo = BlacklistedTokenRepository(session)
    if await blacklisted_repo.exists(
            token=token,
        ):
        logger.exception("Authorization Failed (Token Revoked)")
        raise RevokedAuthTokenError
    
    start_index = request.url.path.find("/")
    end_index = request.url.path.find("/", start_index + 1)
    aud = request.url.path[start_index + 1:end_index]
    if not await jwt_service.verify_token(token=token, aud=[aud, 'admin']):
        logger.exception("Authorization Failed")
        raise IncorrectAuthTokenError
    else:
        logger.info("Authorization Passed")

