import logging
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError, InvalidKeyError, MissingRequiredClaimError
from fastapi import Request, Depends
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.blacklisted_token import BlacklistedTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.errors.auth_token import (
    IncorrectAuthTokenError
    )
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)


async def access_token_middleware(
        request: Request,
        session: AsyncSession = Depends(provide_async_session_stub)
) -> Any:
    aud = ''
    if request.method == 'GET':
        aud = "oidc:admin:read"
    else:
        aud = "oidc:admin:write"

    jwt_service = JWTService()
    token = request.headers.get("access-token")
    blacklisted_repo = BlacklistedTokenRepository(session)
    
    if token is None:
        raise IncorrectAuthTokenError("No access token in Request")
    if await blacklisted_repo.exists(token=token):
        raise IncorrectAuthTokenError("Access Token revoked")
    try:
        await jwt_service.decode_token(token, audience=aud)
    except (InvalidAudienceError, MissingRequiredClaimError):
        raise IncorrectAuthTokenError("Access Token doesn't have admin permissions")
    except ExpiredSignatureError:
        raise IncorrectAuthTokenError("Access Token expired")
    except InvalidKeyError:
        raise IncorrectAuthTokenError("Access Token can not be decoded with our private key")
    except:
        raise IncorrectAuthTokenError("Access Token can not be decoded")

    logger.info("Access Token Auth Passed")
