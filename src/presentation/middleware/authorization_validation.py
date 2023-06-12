import logging
from typing import Any
from fastapi import Request
from src.data_access.postgresql.errors.auth_token import IncorrectAuthTokenError
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError, InvalidKeyError, MissingRequiredClaimError


logger = logging.getLogger(__name__)

async def authorization_middleware(request: Request) -> Any:
    jwt_service = JWTService()
    token = request.headers.get("authorization") or request.headers.get("auth-swagger")
    if token is None:
        raise IncorrectAuthTokenError("No authorization or auth-swagger in Request")

    session = request.state.session
    blacklisted_repo = BlacklistedTokenRepository(session)
    if await blacklisted_repo.exists(
            token=token,
        ):
        raise IncorrectAuthTokenError("Authorization Token is Revoked")
    
    start_index = request.url.path.find("/")
    end_index = request.url.path.find("/", start_index + 1)
    aud = request.url.path[start_index + 1:end_index]
    try:
        if aud == 'revoke':
            aud = 'revocation'
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

