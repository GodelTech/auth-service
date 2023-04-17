import logging
from typing import Union

import jwt
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse

from src.business_logic.endsession.interfaces import EndSessionServiceProtocol
from src.data_access.postgresql.errors.client import (
    ClientPostLogoutRedirectUriError,
)
from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)
from src.di.providers import provide_endsession_service_stub
from src.presentation.api.models.endsession import RequestEndSessionModel

logger = logging.getLogger(__name__)


endsession_router = APIRouter(prefix="/endsession", tags=["End Session"])


@endsession_router.get("/", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(
    request_model: RequestEndSessionModel = Depends(),
    service_class: EndSessionServiceProtocol = Depends(
        provide_endsession_service_stub
    ),
) -> Union[int, RedirectResponse, JSONResponse]:
    try:
        service_class = service_class
        service_class.request_model = request_model
        logout_redirect_uri = await service_class.end_session()
        if logout_redirect_uri is None:
            return status.HTTP_204_NO_CONTENT

        response = RedirectResponse(
            logout_redirect_uri, status_code=status.HTTP_302_FOUND
        )
        return response

    except ClientPostLogoutRedirectUriError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Bad post logout redirect uri"},
        )
    except PersistentGrantNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "You are not logged in"},
        )
    except jwt.exceptions.DecodeError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Bad id_token_hint"},
        )
    except KeyError as exception:
        message = f"KeyError: key {exception} is not in the id_token_hint"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "The id_token_hint is missing something"},
        )
