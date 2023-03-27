import logging
from typing import Any, Dict, Optional, Union
from starlette.templating import _TemplateResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import urllib

from src.business_logic.services import AuthorizationService, LoginFormService
from src.data_access.postgresql.errors import (
    ClientBaseException,
    ClientNotFoundError,
    ClientRedirectUriError,
    UserNotFoundError,
    WrongPasswordError,
    WrongResponseTypeError,
)
from src.presentation.api.routes.utils import (
    InvalidClientResponse,
    UnsupportedResponseTypeRespons,
    UserNotFoundResponse,
    WrongPasswordResponse,
    ClientRedirectUriErrorResponse,
)
from src.di.providers import (
    provide_auth_service_stub,
    provide_login_form_service_stub,
)
from src.dyna_config import BASE_URL
from src.presentation.api.models import DataRequestModel, RequestModel

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="src/presentation/api/templates/")

auth_router = APIRouter(prefix="/authorize", tags=["Authorization"])


@auth_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_authorize(
    request: Request,
    request_model: RequestModel = Depends(),
    auth_class: LoginFormService = Depends(provide_login_form_service_stub),
) -> Union[JSONResponse, _TemplateResponse]:
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        return_form = await auth_class.get_html_form()
        external_logins: Optional[Dict[str, Dict[str, Any]]] = {}
        if request_model.response_type == "code":
            external_logins = await auth_class.form_providers_data_for_auth()

        if return_form:
            return templates.TemplateResponse(
                "login_form.html",
                {
                    "request": request,
                    "request_model": request_model,
                    "external_logins": external_logins,
                    "base_url": BASE_URL,
                },
                status_code=200,
            )
        else:
            raise ValueError
    except (
        ClientBaseException,
        ValueError,
    ) as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        if response_class:
            return response_class()
    except WrongResponseTypeError as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        encoded_error_dict_to_url_query = urllib.parse.urlencode(
            response_class.detail
        )
        response = RedirectResponse(
            f"{request_model.redirect_uri}?{encoded_error_dict_to_url_query}"
        )
        return response


@auth_router.post("/", status_code=status.HTTP_302_FOUND)
async def post_authorize(
    request_body: DataRequestModel = Depends(),
    auth_class: AuthorizationService = Depends(provide_auth_service_stub),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        request_model = RequestModel(**request_body.__dict__)
        auth_class = auth_class
        auth_class.request_model = request_body
        firmed_redirect_uri = await auth_class.get_redirect_url()

        if not firmed_redirect_uri:
            raise UserNotFoundError

        response = RedirectResponse(
            firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except (ClientBaseException, KeyError) as exception:
        logging.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        if response_class:
            return response_class()
    except (UserNotFoundError, WrongPasswordError) as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        encoded_error_dict_to_url_query = urllib.parse.urlencode(
            response_class.detail
        )
        response = RedirectResponse(
            f"{request_model.redirect_uri}?{encoded_error_dict_to_url_query}"
        )
        return response


exception_response_mapper = {
    ClientNotFoundError: InvalidClientResponse,
    ClientRedirectUriError: ClientRedirectUriErrorResponse,
    WrongResponseTypeError: UnsupportedResponseTypeRespons,
    UserNotFoundError: UserNotFoundResponse,
    WrongPasswordError: WrongPasswordResponse,
    KeyError: HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The scope is missing a password, or a username",
    ),
}
