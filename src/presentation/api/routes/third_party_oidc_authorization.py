import logging
from typing import Union

from httpx import AsyncClient
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse


from src.business_logic.third_party_auth import (
    ThirdPartyAuthServiceFactory,
    ThirdPartyAuthServiceProtocol,
)
from src.data_access.postgresql.repositories import (
    ClientRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    PersistentGrantRepository,
)
from src.business_logic.third_party_auth.dto import (
    StateRequestModel,
    ThirdPartyAccessTokenRequestModel,
)


logger = logging.getLogger(__name__)

auth_oidc_router = APIRouter(
    prefix="/authorize/oidc", tags=["OIDC Authorization"]
)


ThirdPartyAuthResponse = Union[RedirectResponse, JSONResponse]


@auth_oidc_router.get(
    "/github",
    status_code=status.HTTP_302_FOUND,
    response_model=None,
)
async def get_github_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> ThirdPartyAuthResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    auth_service: ThirdPartyAuthServiceProtocol = (
        auth_service_factory.get_service_impl("github")
    )
    result = await auth_service.get_redirect_url(request_body)
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)


@auth_oidc_router.get(
    "/linkedin", status_code=status.HTTP_302_FOUND, response_model=None
)
async def get_linkedin_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> ThirdPartyAuthResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    auth_service: ThirdPartyAuthServiceProtocol = (
        auth_service_factory.get_service_impl("linkedin")
    )
    result = await auth_service.get_redirect_url(request_body)
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)


@auth_oidc_router.get(
    "/google",
    status_code=status.HTTP_302_FOUND,
    response_model=None,
)
async def get_google_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> ThirdPartyAuthResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    auth_service: ThirdPartyAuthServiceProtocol = (
        auth_service_factory.get_service_impl("google")
    )
    result = await auth_service.get_redirect_url(request_body)
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)


@auth_oidc_router.get(
    "/gitlab",
    status_code=status.HTTP_302_FOUND,
    response_model=None,
)
async def get_gitlab_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> ThirdPartyAuthResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    auth_service: ThirdPartyAuthServiceProtocol = (
        auth_service_factory.get_service_impl("gitlab")
    )
    result = await auth_service.get_redirect_url(request_body)
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)


@auth_oidc_router.get(
    "/microsoft",
    status_code=status.HTTP_302_FOUND,
    response_model=None,
)
async def get_microsoft_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> ThirdPartyAuthResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    auth_service: ThirdPartyAuthServiceProtocol = (
        auth_service_factory.get_service_impl("microsoft")
    )
    result = await auth_service.get_redirect_url(request_body)
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)


@auth_oidc_router.post(
    "/state",
    status_code=status.HTTP_200_OK,
)
async def post_create_state(
    request: Request,
    request_body: StateRequestModel = Depends(StateRequestModel.as_form),
) -> JSONResponse:
    session = request.state.session
    auth_service_factory = ThirdPartyAuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        async_http_client=AsyncClient(),
    )
    await auth_service_factory.create_provider_state(request_body.state)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "State created successfully"},
    )
