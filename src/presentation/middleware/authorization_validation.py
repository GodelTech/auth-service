import logging
from typing import Any
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol
from src.data_access.postgresql.errors.auth_token import IncorrectAuthTokenError
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from src.di.providers import provide_async_session_stub, provide_jwt_manager
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError, InvalidKeyError, MissingRequiredClaimError


logger = logging.getLogger(__name__)

async def authorization_middleware(
        request: Request,
        session: AsyncSession = Depends(provide_async_session_stub),
        # jwt_manager: JWTManagerProtocol = Depends(provide_jwt_manager),
) -> Any:
    jwt_service = JWTService()
    # jwt_service = provide_jwt_manager(session=session)
    token = request.headers.get("authorization") or request.headers.get("auth-swagger")
    if token is None:
        raise IncorrectAuthTokenError("No authorization or auth-swagger in Request")

    blacklisted_repo = BlacklistedTokenRepository(session)
    if await blacklisted_repo.exists(
            token=token,
        ):
        raise IncorrectAuthTokenError("Authorization Token is Revoked")
    
    start_index = request.url.path.find("/")
    end_index = request.url.path.find("/", start_index + 1)
    aud = request.url.path[start_index + 1:end_index]
    try:
        if aud == "revoke":
            aud = "revocation"
        await jwt_service.decode_token(token=token, audience=[aud, 'admin'])
    except (InvalidAudienceError, MissingRequiredClaimError):
        raise IncorrectAuthTokenError(f"Authorization Token doesn't have {aud} permissions")
    except ExpiredSignatureError:
        raise IncorrectAuthTokenError("Authorization Token expired")
    except InvalidKeyError:
        raise IncorrectAuthTokenError("Authorization Token can not be decoded with our private key")
    except:
        raise IncorrectAuthTokenError("Authorization Token can not be decoded")
    else:
        logger.info("Authorization Passed")

