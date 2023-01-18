import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse

from src.business_logic.services import AuthorizationService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserNotFoundError,
    WrongPasswordError,
)
from src.presentation.api.models import DataRequestModel, RequestModel

logger = logging.getLogger("is_app")


auth_router = APIRouter(
    prefix="/authorize",
)


@auth_router.get("/", status_code=status.HTTP_302_FOUND, tags=["Authorization"])
async def get_authorize(
    request_model: RequestModel = Depends(),
    auth_class: AuthorizationService = Depends(),
):
    try:
        auth_class = auth_class
        auth_class.request_model = request_model
        firmed_redirect_uri = await auth_class.get_redirect_url()
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
    except IndexError as exception:
        message = f"IndexError: {exception} - Impossible to parse the scope"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Impossible to parse the scope"},
        )


@auth_router.post(
    "/", status_code=status.HTTP_302_FOUND, tags=["Authorization"]
)
async def post_authorize(
    request_body: DataRequestModel = Depends(),
    auth_class: AuthorizationService = Depends(),
):
    try:
        request_model = RequestModel(**request_body.__dict__)
        auth_class = auth_class
        auth_class.request_model = request_model
        firmed_redirect_uri = await auth_class.get_redirect_url()
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
    except IndexError as exception:
        message = f"IndexError: {exception} - Impossible to parse the scope"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Impossible to parse the scope"},
        )
