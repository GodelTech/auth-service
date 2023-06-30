import logging
from typing import Any
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.errors.auth_token import IncorrectAuthTokenError
from typing import Any
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import BlacklistedTokenRepository, ResourcesRepository
from src.di.providers import provide_async_session_stub
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError, InvalidKeyError, MissingRequiredClaimError


logger = logging.getLogger(__name__)

OIDC_RESOURCE_NAME = 'oidc'
OIDC_USERINFO_ROUTE_NAME = 'userinfo'

async def authorization_middleware(
        request: Request,
        session: AsyncSession = Depends(provide_async_session_stub),
) -> Any:
    jwt_service = JWTService()
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
    route = request.url.path[start_index + 1:end_index]
    aud = await get_aud(session=session, route = route)
    try:
        await jwt_service.decode_token(token=token, audience=aud)
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

async def get_aud(session:AsyncSession, route:str):
    res_repo = ResourcesRepository(session)
    if route == OIDC_USERINFO_ROUTE_NAME:
        return await res_repo.get_scope_claims(resource_name=OIDC_RESOURCE_NAME, scope_name=route)
    else:
        scope_claims_types =  await res_repo.get_scope_claims(resource_name=OIDC_RESOURCE_NAME, scope_name=route)
        return [f'{OIDC_RESOURCE_NAME}:{route}:{claim_type}' for claim_type in scope_claims_types]