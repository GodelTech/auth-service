from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from src.business_logic.authorization import AuthServiceFactory
from src.business_logic.authorization.dto import AuthRequestModel
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.login_form_service import LoginFormService
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.repositories import (
    ClientRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository, CodeChallengeRepository,
)
from src.dyna_config import DOMAIN_NAME
from src.presentation.api.models import RequestModel

if TYPE_CHECKING:
    from src.business_logic.authorization import AuthServiceProtocol

AuthorizePostEndpointResponse = Union[RedirectResponse, JSONResponse]
AuthorizeGetEndpointResponse = Union[JSONResponse, _TemplateResponse]

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="src/presentation/api/templates/")

auth_router = APIRouter(prefix="/authorize", tags=["Authorization"])


@auth_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
    response_model=None,
)
async def get_authorize(
    request: Request,
    request_model: RequestModel = Depends(),
) -> AuthorizeGetEndpointResponse:
    session = request.state.session
    auth_class = LoginFormService(
        session=session,
        client_repo=ClientRepository(session),
        oidc_repo=ThirdPartyOIDCRepository(session),
        code_challenge_repo=CodeChallengeRepository(session),
    )
    auth_class.request_model = request_model
    return_form = await auth_class.get_html_form()
    external_logins: Optional[dict[str, dict[str, Any]]] = {}
    if request_model.response_type == "code":
        external_logins = await auth_class.form_providers_data_for_auth()

    if return_form:
        return templates.TemplateResponse(
            "login_form.html",
            {
                "request": request,
                "request_model": request_model,
                "external_logins": external_logins,
                "base_url": DOMAIN_NAME,
            },
            status_code=200,
        )
    else:
        raise ValueError


@auth_router.post("/", status_code=status.HTTP_302_FOUND, response_model=None)
async def post_authorize(
    request: Request,
    request_body: AuthRequestModel = Depends(AuthRequestModel.as_form),
    user_code: Optional[str] = Cookie(None),
) -> AuthorizePostEndpointResponse:
    session = request.state.session
    auth_service_factory = AuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        device_repo=DeviceRepository(session),
        password_service=PasswordHash(),
        jwt_service=JWTService(),
    )
    setattr(request_body, "user_code", user_code)
    auth_service: AuthServiceProtocol = auth_service_factory.get_service_impl(
        request_body.response_type
    )
    result = await auth_service.get_redirect_url(request_body)
    await session.commit()
    return RedirectResponse(result, status_code=status.HTTP_302_FOUND)
