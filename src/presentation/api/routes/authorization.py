import logging
from typing import Any, Dict, Optional, Union
from starlette.templating import _TemplateResponse
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.business_logic.services import AuthorizationService, LoginFormService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
    UserNotFoundError,
    WrongPasswordError,
    WrongResponseTypeError,
)
from src.di.providers import (
    provide_auth_service_stub,
    provide_login_form_service_stub,
)
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
) -> Union[JSONResponse, _TemplateResponse] :
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
                },
                status_code=200,
            )
        else:
            raise ValueError

    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except ClientRedirectUriError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Redirect Uri not found"},
        )
    except WrongResponseTypeError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Bad response type"},
        )


@auth_router.post("/", status_code=status.HTTP_302_FOUND)
async def post_authorize(
    request_body: DataRequestModel = Depends(),
    auth_class: AuthorizationService = Depends(provide_auth_service_stub),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        request_model = RequestModel(**request_body.__dict__)
        auth_class = auth_class
        auth_class.request_model = request_model
        await auth_class.save_code_challenge_data()

        firmed_redirect_uri = await auth_class.get_redirect_url()
        
        if not firmed_redirect_uri:
            raise UserNotFoundError
        
        response = RedirectResponse(
            firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        )

        return response
    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except UserNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"},
        )
    except WrongPasswordError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Bad password"},
        )
    except KeyError as exception:
        message = (
            f"KeyError: key {exception} does not exist is not in the scope"
        )
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "The scope is missing a password, or a username"
            },
        )
