import logging
from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.third_party_oidc_service import (
    AuthThirdPartyOIDCService,
    ThirdPartyFacebookService,
    ThirdPartyGoogleService,
    ThirdPartyLinkedinService,
    ThirdPartyGitLabService,
    ThirdPartyMicrosoftService,
)
from src.data_access.postgresql.errors import (
    WrongDataError,
)
from src.data_access.postgresql.errors.third_party_oidc import ParsingError
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    ThirdPartyOIDCRepository,
    PersistentGrantRepository,
)
from src.presentation.api.models import (
    StateRequestModel,
    ThirdPartyFacebookRequestModel,
    ThirdPartyGoogleRequestModel,
    ThirdPartyLinkedinRequestModel,
    ThirdPartyOIDCRequestModel,
    ThirdPartyMicrosoftRequestModel,
)
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

auth_oidc_router = APIRouter(
    prefix="/authorize/oidc", tags=["OIDC Authorization"]
)


# http://127.0.0.1:8000/authorize/oidc/github


@auth_oidc_router.get(
    "/github", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_github_authorize(
    request: Request,
    request_model: ThirdPartyOIDCRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = AuthThirdPartyOIDCService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.get(
    "/linkedin", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_linkedin_authorize(
    request: Request,
    request_model: ThirdPartyLinkedinRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = ThirdPartyLinkedinService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.get(
    "/facebook", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_facebook_authorize(
    request: Request,
    request_model: ThirdPartyFacebookRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = ThirdPartyFacebookService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.get(
    "/google", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_google_authorize(
    request: Request,
    request_model: ThirdPartyGoogleRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = ThirdPartyGoogleService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.get(
    "/gitlab", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_gitlab_authorize(
    request: Request,
    request_model: ThirdPartyOIDCRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = ThirdPartyGitLabService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.get(
    "/microsoft", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_microsoft_authorize(
    request: Request,
    request_model: ThirdPartyMicrosoftRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = session
        auth_class = ThirdPartyMicrosoftService(
            session=session,
            client_repo=ClientRepository(session),
            user_repo=UserRepository(session),
            persistent_grant_repo=PersistentGrantRepository(session),
            oidc_repo=ThirdPartyOIDCRepository(session),
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
        await session.commit()
        return response

    except IndexError:
        raise ParsingError


@auth_oidc_router.post(
    "/state", status_code=status.HTTP_200_OK, response_model=None
)
async def post_create_state(
    request: Request,
    state_request_model: StateRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[None, JSONResponse, int]:
    session = session
    auth_class = AuthThirdPartyOIDCService(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
    )
    auth_class.state_request_model = state_request_model
    await auth_class.create_provider_state()
    return status.HTTP_200_OK
