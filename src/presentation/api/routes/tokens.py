import logging
from typing import Any, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.business_logic.services import TokenService
from src.data_access.postgresql.errors import (
    ClientGrantsError,
    ClientNotFoundError,
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
        return result

    except ClientNotFoundError as e:
        logger.exception(e)
        return JSONResponse(
            content={
                "error": "invalid_client",
                "error_description": "Client authentication failed.",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except ClientGrantsError as e:
        logger.exception(e)
        return JSONResponse(
            content={
                "error": "unauthorized_client",
                "error_description": "The client is not authorized to use requested grant type.",
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except GrantNotFoundError as e:
        logger.exception(e)
        return JSONResponse(
            content={
                "error": "invalid_grant",
                "error_description": "The authorization code is invalid or expired.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except GrantTypeNotSupported as e:
        logger.exception(e)
        return JSONResponse(
            content={
                "error": "unsupported_grant_type",
                "error_description": "Requested grant_type was not recognized by the server.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
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
        return JSONResponse(
            content={
                "error": "invalid_request",
                "error_description": "Request was missing required parameter(s).",
            }
        )
