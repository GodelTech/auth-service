import logging
from typing import Union

from httpx import AsyncClient
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.business_logic.services import ThirdPartyFacebookService
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
from src.data_access.postgresql.errors import WrongDataError
from src.di.providers import (
    provide_third_party_auth_service_factory_stub,
    provide_third_party_facebook_service_stub,
)
from src.presentation.api.models import ThirdPartyFacebookRequestModel

logger = logging.getLogger(__name__)

auth_oidc_router = APIRouter(
    prefix="/authorize/oidc", tags=["OIDC Authorization"]
)


@auth_oidc_router.get(
    "/github",
    status_code=status.HTTP_302_FOUND,
)
async def get_github_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
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


@auth_oidc_router.get("/linkedin", status_code=status.HTTP_302_FOUND)
async def get_linkedin_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
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
)
async def get_google_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
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
)
async def get_gitlab_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
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
)
async def get_microsoft_authorize(
    request: Request,
    request_body: ThirdPartyAccessTokenRequestModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
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


# @auth_oidc_router.get( # TODO not implemented because of https
#     "/facebook",
#     status_code=status.HTTP_302_FOUND,
# )
# async def get_facebook_authorize(
#     request_model: ThirdPartyFacebookRequestModel = Depends(),
#     auth_class: ThirdPartyFacebookService = Depends(
#         provide_third_party_facebook_service_stub
#     ),
# ) -> Union[RedirectResponse, JSONResponse]:
#     try:
#         auth_class.request_model = request_model
#         github_redirect_uri = await auth_class.get_facebook_redirect_uri(
#             provider_name="facebook"
#         )
#         if github_redirect_uri is None:
#             raise WrongDataError
#         return RedirectResponse(
#             github_redirect_uri, status_code=status.HTTP_302_FOUND
#         )

#     except WrongDataError as exception:
#         logger.exception(exception)
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content={"message": "Wrong data has been passed"},
#         )
#     except IndexError as exception:
#         logger.exception(exception)
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content={"message": "Error in parsing"},
#         )
