import logging
from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from data_access.postgresql.errors.device import DeviceBaseException
from src.data_access.postgresql.errors import ClientBaseException
from src.business_logic.services import DeviceService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserCodeNotFoundError,
)
from src.presentation.api.routes.utils import (
    InvalidClientResponse,
    UserCodeNotFoundErrorResponse,
)
from src.di.providers import provide_device_service_stub
from src.presentation.api.models import (
    DeviceCancelModel,
    DeviceRequestModel,
    DeviceUserCodeModel,
)

logger = logging.getLogger("is_app")

templates = Jinja2Templates(directory="src/presentation/api/templates/")

device_auth_router = APIRouter(prefix="/device", tags=["Device"])


@device_auth_router.post(
    "/", status_code=status.HTTP_200_OK, response_class=JSONResponse
)
async def post_device_authorize(
    request_model: DeviceRequestModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),
) -> JSONResponse:
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        response_data = await auth_service.get_response()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data,
        )

    except ClientBaseException as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        if response_class:
            return response_class()


@device_auth_router.get(
    "/auth",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_device_user_code(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse(
        "device_login_form.html", {"request": request}, status_code=200
    )


@device_auth_router.post("/auth", status_code=status.HTTP_302_FOUND)
async def post_device_user_code(
    request_model: DeviceUserCodeModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        firmed_redirect_uri = await auth_service.get_redirect_uri()

        response = RedirectResponse(
            firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except DeviceBaseException as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        if response_class:
            return response_class()


@device_auth_router.get(
    "/auth/success",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_device_login_confirm(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse(
        "device_confirmed_form.html", {"request": request}, status_code=200
    )


@device_auth_router.delete("/auth/cancel", status_code=status.HTTP_200_OK)
async def delete_device(
    request_model: DeviceCancelModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),
) -> Union[str, JSONResponse]:
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        firmed_redirect_uri = await auth_service.clean_device_data()

        return firmed_redirect_uri

    except (ClientBaseException, DeviceBaseException) as exception:
        logger.exception(exception)
        response_class = exception_response_mapper.get(type(exception))
        if response_class:
            return response_class()


@device_auth_router.get(
    "/auth/cancel",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_device_cancel_form(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse(
        "cancel_device_form.html", {"request": request}, status_code=200
    )


exception_response_mapper = {
    ClientNotFoundError: InvalidClientResponse,
    UserCodeNotFoundError: UserCodeNotFoundErrorResponse,
}
