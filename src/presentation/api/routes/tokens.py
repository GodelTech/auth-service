import logging
from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from src.di.providers import provide_token_service_factory_stub
from src.business_logic.get_tokens.dto import ResponseTokenModel, RequestTokenModel
from src.business_logic.get_tokens import TokenServiceFactory

from typing import Union, Any, TYPE_CHECKING
# if TYPE_CHECKING:
#     from src.business_logic.get_tokens.interfaces import TokenServiceProtocol


TokenEndpointResponse = Union[JSONResponse, dict[str, Any]]


from src.business_logic.services import TokenService
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
from src.di.providers import provide_token_service_stub
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


@token_router.post("/")
async def get_tokens(
        request_body: RequestTokenModel = Depends(),
        token_service_factory: TokenServiceFactory = Depends(provide_token_service_factory_stub),
) -> TokenEndpointResponse:
    token_service: 'TokenServiceProtocol' = token_service_factory.get_service_impl(request_body.grant_type)
    result: ResponseTokenModel = await token_service.get_tokens(request_body)
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    return JSONResponse(content=result.dict(exclude_none=True), headers=headers)

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
        else:
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
