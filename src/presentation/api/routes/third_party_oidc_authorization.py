import logging
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from httpx import AsyncClient

from src.business_logic.services import (
    AuthThirdPartyOIDCService,
    ThirdPartyFacebookService,
    ThirdPartyGitLabService,
    ThirdPartyGoogleService,
    ThirdPartyLinkedinService,
    ThirdPartyGitLabService,
    ThirdPartyMicrosoftService,
)
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ThirdPartyStateDuplicationError,
    ThirdPartyStateNotFoundError,
    WrongDataError,
)
from src.di.providers import (
    provide_auth_third_party_linkedin_service_stub,
    provide_auth_third_party_oidc_service_stub,
    provide_third_party_facebook_service_stub,
    provide_third_party_gitlab_service_stub,
    provide_third_party_google_service_stub,
    provide_third_party_microsoft_service_stub,
)
from src.presentation.api.models import (
    StateRequestModel,
    ThirdPartyFacebookRequestModel,
    ThirdPartyGoogleRequestModel,
    ThirdPartyLinkedinRequestModel,
    ThirdPartyOIDCRequestModel,
    ThirdPartyMicrosoftRequestModel,
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
        github_redirect_uri = await auth_class.get_github_redirect_uri(
            provider_name="github"
        )
        if github_redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            github_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
        )


@auth_oidc_router.get("/linkedin", status_code=status.HTTP_302_FOUND)
async def get_linkedin_authorize(
    request_model: ThirdPartyLinkedinRequestModel = Depends(),
    auth_class: ThirdPartyLinkedinService = Depends(
        provide_auth_third_party_linkedin_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        linkedin_redirect_uri = await auth_class.get_redirect_uri(
            provider_name="linkedin"
        )
        if linkedin_redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            linkedin_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
        )


@auth_oidc_router.get(
    "/facebook",
    status_code=status.HTTP_302_FOUND,
)
async def get_facebook_authorize(
    request_model: ThirdPartyFacebookRequestModel = Depends(),
    auth_class: ThirdPartyFacebookService = Depends(
        provide_third_party_facebook_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        github_redirect_uri = await auth_class.get_facebook_redirect_uri(
            provider_name="facebook"
        )
        if github_redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            github_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
        )


@auth_oidc_router.get(
    "/google",
    status_code=status.HTTP_302_FOUND,
)
async def get_google_authorize(
    request_model: ThirdPartyGoogleRequestModel = Depends(),
    auth_class: ThirdPartyGoogleService = Depends(
        provide_third_party_google_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        github_redirect_uri = await auth_class.get_google_redirect_uri(
            provider_name="google"
        )
        if github_redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            github_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
        )


@auth_oidc_router.get(
    "/gitlab",
    status_code=status.HTTP_302_FOUND,
)
async def get_gitlab_authorize(
    request_model: ThirdPartyOIDCRequestModel = Depends(),
    auth_class: ThirdPartyGitLabService = Depends(
        provide_third_party_gitlab_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        github_redirect_uri = await auth_class.get_redirect_uri(
            provider_name="gitlab"
        )
        if github_redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            github_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
        )


@auth_oidc_router.get(
    "/microsoft",
    status_code=status.HTTP_302_FOUND,
)
async def get_microsoft_authorize(
    request_model: ThirdPartyMicrosoftRequestModel = Depends(),
    auth_class: ThirdPartyMicrosoftService = Depends(
        provide_third_party_microsoft_service_stub
    ),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        redirect_uri = await auth_class.get_redirect_uri(
            provider_name="microsoft"
        )
        if redirect_uri is None:
            raise WrongDataError
        response = RedirectResponse(
            redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except WrongDataError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong data has been passed"},
        )
    except IndexError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Error in parsing"},
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
) -> Union[None, JSONResponse, int]:
    try:
        auth_class = auth_class
        auth_class.state_request_model = state_request_model
        await auth_class.create_provider_state()
        return status.HTTP_200_OK

    except ThirdPartyStateDuplicationError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Third Party State already exists"},
        )
