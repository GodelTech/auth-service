import logging

from fastapi import Request
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.blacklisted_token import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.errors.auth_token import (
    NoAuthTokenError, 
    RevokedAuthTokenError,
    IncorrectAuthTokenError
    )

logger = logging.getLogger(__name__)


async def access_token_middleware(request: Request) -> Any:
    jwt_service = JWTService()
    token = request.headers.get("access-token")
    session = request.state.session
    blacklisted_repo = BlacklistedTokenRepository(session)
    
    if token is None:
        raise NoAuthTokenError
    if await blacklisted_repo.exists(token=token):
        raise RevokedAuthTokenError

    if not await jwt_service.verify_token(token, aud='admin'):
            raise IncorrectAuthTokenError

    logger.info("Access Token Auth Passed")
