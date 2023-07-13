from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.authorization import AuthServiceFactory
from src.business_logic.authorization.dto import AuthRequestModel
from src.business_logic.jwt_manager import JWTManager
from src.business_logic.services.login_form_service import LoginFormService
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.repositories import (
    ClientRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    PersistentGrantRepository,
    DeviceRepository,
    ResourcesRepository,
    CodeChallengeRepository,
)
from src.business_logic.authorization import AuthServiceFactory
from src.business_logic.authorization.dto import AuthRequestModel
from src.business_logic.services.login_form_service import LoginFormService
from src.business_logic.services.scope import ScopeService
from src.business_logic.services.jwt_token import JWTService
from src.dyna_config import DOMAIN_NAME
from src.presentation.api.models import RequestModel
from src.di.providers import provide_async_session_stub

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
    session: AsyncSession = Depends(provide_async_session_stub),
) -> AuthorizeGetEndpointResponse:
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

    scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session
        )
    
    confirm_text = await scope_service.get_scope_description(scope=request_model.scope)
    # confirm_text = print_items(confirm_text)
    header_text = 'The service want to get access to:'
    if return_form:
        return templates.TemplateResponse(
            "login_form.html",
            {
                "confirm_text":confirm_text, 
                "confirm_header":header_text,
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
    session: AsyncSession = Depends(provide_async_session_stub),
) -> AuthorizePostEndpointResponse:
    auth_service_factory = AuthServiceFactory(
        session=session,
        client_repo=ClientRepository(session),
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        device_repo=DeviceRepository(session),
        password_service=PasswordHash(),
        jwt_service=JWTService(),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session
        )
    )
    setattr(request_body, "user_code", user_code)
    auth_service: AuthServiceProtocol = auth_service_factory.get_service_impl(
        request_body.response_type
    )
    result = await auth_service.get_redirect_url(request_body)
    await session.commit()
    
    return RedirectResponse(url=result, status_code=302)



# def print_items(confirm_text:dict, style="list-style-type:circle"):
#     result = '<ul> '
#     for k in confirm_text:
#         result += f"<li> {k} </li> "
#         if type(confirm_text[k]) is dict:
#            result += print_items(confirm_text[k])
#         if type(confirm_text[k]) is str:
#             result += f"<ul> <li> {confirm_text[k]} </li> </ul> "
#     return result + ' </ul>'