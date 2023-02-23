import logging
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from httpx import AsyncClient

from src.business_logic.services import AuthThirdPartyOIDCService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ThirdPartyStateNotFoundError,
    ThirdPartyStateDuplicationError,
)
from src.di.providers import provide_auth_third_party_oidc_service_stub
from src.presentation.api.models import (
    ThirdPartyOIDCRequestModel,
    StateRequestModel,
)

logger = logging.getLogger(__name__)

auth_oidc_router = APIRouter(
    prefix="/authorize/oidc", tags=["OIDC Authorization"]
)

# http://127.0.0.1:8000/authorize/oidc/github


@auth_oidc_router.get(
    "/github",
    status_code=status.HTTP_302_FOUND,
)
async def get_github_authorize(
    request_model: ThirdPartyOIDCRequestModel = Depends(),
    auth_class: AuthThirdPartyOIDCService = Depends(
        provide_auth_third_party_oidc_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        github_redirect_uri = await auth_class.get_github_redirect_uri()
        response = RedirectResponse(
            github_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except ThirdPartyStateNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Third Party State not found"},
        )
    except ThirdPartyStateDuplicationError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Third Party State already exists"},
        )


@auth_oidc_router.post(
    "/state",
    status_code=status.HTTP_200_OK,
)
async def post_create_state(
    state_request_model: StateRequestModel = Depends(),
    auth_class: AuthThirdPartyOIDCService = Depends(
        provide_auth_third_party_oidc_service_stub
    ),
) -> Union[None, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.state_request_model = state_request_model
        await auth_class.create_provider_state()
        return status.HTTP_200_OK

    except ThirdPartyStateDuplicationError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Third Party State already exists"},
        )
