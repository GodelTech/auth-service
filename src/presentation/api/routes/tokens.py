import logging
from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
    DeviceRepository,
    BlacklistedTokenRepository
)
from src.business_logic.services import TokenService, JWTService
from src.data_access.postgresql.errors import (
    ClientBaseException,
    ClientGrantsError,
    ClientNotFoundError,
    ClientScopesError,
    ClientRedirectUriError,
    DeviceBaseException,
    DeviceCodeExpirationTimeError,
    DeviceCodeNotFoundError,
    DeviceRegistrationError,
    GrantBaseException,
    GrantNotFoundError,
    GrantTypeNotSupported,
)
from src.presentation.api.models.tokens import (
    BodyRequestTokenModel,
    ResponseTokenModel,
)
from src.presentation.api.routes.utils import (
    InvalidClientResponse,
    InvalidGrantResponse,
    InvalidRequestResponse,
    InvalidScopeResponse,
    UnauthorizedClientResponse,
    UnsupportedGrantTypeResponse,
)

logger = logging.getLogger(__name__)


token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post("/", response_model=ResponseTokenModel)

async def get_tokens(
    request: Request,
    request_body: BodyRequestTokenModel = Depends(),    
) -> Union[JSONResponse, Dict[str, Any]]:
    try:
        session = request.state.session
        token_class = TokenService(
            session = session,
            client_repo=ClientRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            user_repo=UserRepository(session),
            device_repo=DeviceRepository(session),
            blacklisted_repo=BlacklistedTokenRepository(session)
            )
        token_class.request = request
        token_class.request_model = request_body
        result = await token_class.get_tokens()
        headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
        return JSONResponse(content=result, headers=headers)

    except (
        DeviceBaseException,
        ClientBaseException,
        GrantBaseException,
        ValueError,
    ) as e:
        logger.exception(e)
        response_class = exception_response_mapper.get(type(e))
        if response_class:
            return response_class()
        raise e

    except Exception as e:
        logger.exception(e)
        raise e


exception_response_mapper = {
    ClientNotFoundError: InvalidClientResponse,
    ClientGrantsError: UnauthorizedClientResponse,
    ClientScopesError: InvalidScopeResponse,
    ClientRedirectUriError: InvalidGrantResponse,
    GrantNotFoundError: InvalidGrantResponse,
    GrantTypeNotSupported: UnsupportedGrantTypeResponse,
    DeviceCodeExpirationTimeError: HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Device code expired"
    ),
    DeviceRegistrationError: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Device registration in progress",
    ),
    DeviceCodeNotFoundError: HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Such device code does not exist",
    ),
    ValueError: InvalidRequestResponse,
}
