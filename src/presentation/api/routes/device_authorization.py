import logging

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.business_logic.services import DeviceService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserCodeNotFoundError,
)
from src.presentation.api.models import DeviceRequestModel, DeviceUserCodeModel, DeviceCancelModel
from src.di.providers import provide_device_service_stub


logger = logging.getLogger("is_app")

templates = Jinja2Templates(directory="src/presentation/api/templates/")

device_auth_router = APIRouter(
    prefix="/device",
)


@device_auth_router.post("/", status_code=status.HTTP_200_OK, tags=["Device"], response_class=JSONResponse)
async def post_device_authorize(
    request_model: DeviceRequestModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),
):
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        response_data = await auth_service.get_response()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data,
        )

    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )


@device_auth_router.get("/auth", status_code=status.HTTP_200_OK, tags=["Device"], response_class=HTMLResponse)
async def get_device_user_code(
    request: Request,
):
    return templates.TemplateResponse(
        "device_login_form.html",
        {"request": request},
        status_code=200
    )


@device_auth_router.post("/auth", status_code=status.HTTP_302_FOUND, tags=["Device"])
async def post_device_user_code(
    request_model: DeviceUserCodeModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),

):
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        firmed_redirect_uri = await auth_service.get_redirect_uri()

        response = RedirectResponse(
            firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except UserCodeNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong user code"},
        )


@device_auth_router.get("/auth/success", status_code=status.HTTP_200_OK, tags=["Device"], response_class=HTMLResponse)
async def get_device_login_confirm(
    request: Request,
):
    return templates.TemplateResponse(
        "device_confirmed_form.html",
        {"request": request},
        status_code=200
    )


@device_auth_router.post("/auth/cancel", status_code=status.HTTP_302_FOUND, tags=["Device"])
async def post_device_cancel(
    request_model: DeviceCancelModel = Depends(),
    auth_service: DeviceService = Depends(provide_device_service_stub),
):
    try:
        auth_service = auth_service
        auth_service.request_model = request_model
        firmed_redirect_uri = await auth_service.clean_device_data()

        # response = RedirectResponse(
        #     firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        # )
        # return response
        return

    except UserCodeNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong user code"},
        )
    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )


@device_auth_router.get("/auth/cancel", status_code=status.HTTP_200_OK, tags=["Device"], response_class=HTMLResponse)
async def get_device_cancel(
    request: Request,
):
    return templates.TemplateResponse(
        "cancel_device_form.html",
        {"request": request},
        status_code=200
    )
