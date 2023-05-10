import logging
from typing import Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.repositories import ClientRepository, DeviceRepository
from src.business_logic.services import DeviceService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserCodeNotFoundError,
)
from src.dyna_config import BASE_URL_HOST
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
    request:Request,
    request_model: DeviceRequestModel = Depends(),
) -> JSONResponse:
    session = request.state.session
    auth_service = DeviceService(
        client_repo=ClientRepository(session=session),
        device_repo=DeviceRepository(session=session),
        session=session
    )
    try:
        auth_service.request_model = request_model
        response_data = await auth_service.get_response()
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data,
        )
    except ClientNotFoundError as exception:
        logger.exception(exception)
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


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
    "/auth", status_code=status.HTTP_302_FOUND, response_class=RedirectResponse
)
async def post_device_user_code(
    request:Request,
    request_model: DeviceUserCodeModel = Depends(),
) -> Union[RedirectResponse, JSONResponse]:
    try:
        session = request.state.session
        auth_service = DeviceService(
            client_repo=ClientRepository(session=session),
            device_repo=DeviceRepository(session=session),
            session=session
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

    except UserCodeNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong user code"},
        )



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
    request:Request,
    request_model: DeviceCancelModel = Depends(),
    user_code: Optional[str] = Cookie(None),  
) -> Union[str, JSONResponse]:
    session = request.state.session
    auth_service = DeviceService(session)
    try:
        auth_service.request_model = request_model
        result = await auth_service.clean_device_data(user_code)
        await session.commit()
        return result
    except UserCodeNotFoundError as exception:
        logger.exception(exception)
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Wrong user code"},
        )
    except ClientNotFoundError as exception:
        logger.exception(exception)
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


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
