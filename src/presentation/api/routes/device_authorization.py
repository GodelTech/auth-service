import logging
from typing import Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.device_auth import DeviceService
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
)
from src.dyna_config import BASE_URL_HOST
from src.presentation.api.models import (
    DeviceCancelModel,
    DeviceRequestModel,
    DeviceUserCodeModel,
)
from src.di.providers import provide_async_session_stub

logger = logging.getLogger("is_app")

templates = Jinja2Templates(directory="src/presentation/api/templates/")

device_auth_router = APIRouter(prefix="/device", tags=["Device"])


@device_auth_router.post(
    "/", status_code=status.HTTP_200_OK, response_class=JSONResponse
)
async def post_device_authorize(
    request: Request,
    request_model: DeviceRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> JSONResponse:
    auth_service = DeviceService(
        session=session,
        client_repo=ClientRepository(session),
        device_repo=DeviceRepository(session),
    )
    auth_service.request_model = request_model
    response_data = await auth_service.get_response()
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data,
    )


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


@device_auth_router.post(
    "/auth",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    response_model=None,
)
async def post_device_user_code(
    request: Request,
    request_model: DeviceUserCodeModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[RedirectResponse, JSONResponse]:
    auth_service = DeviceService(
        session=session,
        client_repo=ClientRepository(session),
        device_repo=DeviceRepository(session),
    )
    auth_service.request_model = request_model
    firmed_redirect_uri = await auth_service.get_redirect_uri()

    response = RedirectResponse(
        firmed_redirect_uri, status_code=status.HTTP_302_FOUND
    )

    response.set_cookie(
        key="user_code",
        value=request_model.user_code,
        expires=600,
        domain=BASE_URL_HOST,
        httponly=True,
    )  # TODO add secure=True when we'll have https
    return response


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


@device_auth_router.delete(
    "/auth/cancel", status_code=status.HTTP_200_OK, response_model=None
)
async def delete_device(
    request: Request,
    request_model: DeviceCancelModel = Depends(),
    user_code: Optional[str] = Cookie(None),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[str, JSONResponse]:
    auth_service = DeviceService(
        session=session,
        client_repo=ClientRepository(session),
        device_repo=DeviceRepository(session),
    )
    auth_service.request_model = request_model
    user_code = request_model.scope.split("=")[1]
    result = await auth_service.clean_device_data(user_code)
    await session.commit()
    return result



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
