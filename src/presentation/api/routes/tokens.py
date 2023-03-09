import logging
from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.business_logic.services import TokenService
from src.data_access.postgresql.errors import (
    ClientGrantsError,
    ClientNotFoundError,
    ClientScopesError,
    DeviceCodeExpirationTimeError,
    DeviceCodeNotFoundError,
    DeviceRegistrationError,
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


@token_router.post("/", response_model=ResponseTokenModel)
async def get_tokens(
    request: Request,
    request_body: BodyRequestTokenModel = Depends(),
    token_class: TokenService = Depends(provide_token_service_stub),
) -> Union[JSONResponse, Dict[str, Any]]:
    try:
        token_class = token_class
        token_class.request = request
        token_class.request_model = request_body
        result = await token_class.get_tokens()
        headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
        return JSONResponse(content=result, headers=headers)

    except ClientNotFoundError as e:
        logger.exception(e)
        return InvalidClientResponse()

    except ClientGrantsError as e:
        logger.exception(e)
        return UnauthorizedClientResponse()

    except ClientScopesError as e:
        logger.exception(e)
        return InvalidScopeResponse()

    except GrantNotFoundError as e:
        logger.exception(e)
        return InvalidGrantResponse()

    except GrantTypeNotSupported as e:
        logger.exception(e)
        return UnsupportedGrantTypeResponse()

    except DeviceCodeExpirationTimeError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Device code expired"
        )
    except DeviceRegistrationError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device registration in progress",
        )
    except DeviceCodeNotFoundError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Such device code does not exist",
        )
    except ValueError as e:
        logger.exception(e)
        return InvalidRequestResponse()
