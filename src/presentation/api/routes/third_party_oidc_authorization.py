import logging
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
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
from src.presentation.api.models import (
    StateRequestModel,
    ThirdPartyFacebookRequestModel,
    ThirdPartyGoogleRequestModel,
    ThirdPartyLinkedinRequestModel,
    ThirdPartyOIDCRequestModel,
    ThirdPartyMicrosoftRequestModel,
)
from src.data_access.postgresql.repositories import ClientRepository, UserRepository, ThirdPartyOIDCRepository, PersistentGrantRepository


logger = logging.getLogger(__name__)

auth_oidc_router = APIRouter(
    prefix="/authorize/oidc", tags=["OIDC Authorization"]
)

# http://127.0.0.1:8000/authorize/oidc/github


@auth_oidc_router.get(
    "/github",
    status_code=status.HTTP_302_FOUND,
    response_model=None
)

async def get_github_authorize(
    request:Request,
    request_model: ThirdPartyOIDCRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = AuthThirdPartyOIDCService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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


@auth_oidc_router.get("/linkedin", status_code=status.HTTP_302_FOUND, response_model=None)
async def get_linkedin_authorize(
    request:Request,
    request_model: ThirdPartyLinkedinRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = ThirdPartyLinkedinService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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
    response_model=None
)

async def get_facebook_authorize(
    request:Request,
    request_model: ThirdPartyFacebookRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = ThirdPartyFacebookService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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
    response_model=None
)

async def get_google_authorize(
    request:Request,
    request_model: ThirdPartyGoogleRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = ThirdPartyGoogleService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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
    response_model=None
)

async def get_gitlab_authorize(
    request:Request,
    request_model: ThirdPartyOIDCRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = ThirdPartyGitLabService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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
    response_model=None
)

async def get_microsoft_authorize(
    request:Request,
    request_model: ThirdPartyMicrosoftRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_class = ThirdPartyMicrosoftService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
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
    response_model=None
)

async def post_create_state(
    request:Request,
    state_request_model: StateRequestModel = Depends(),
) -> Union[None, JSONResponse, int]:
    try:
        session = request.state.session
        auth_class = AuthThirdPartyOIDCService(
            session = session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session)
            )
        auth_class.state_request_model = state_request_model
        await auth_class.create_provider_state()
        return status.HTTP_200_OK

    except ThirdPartyStateDuplicationError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Third Party State already exists"},
        )
