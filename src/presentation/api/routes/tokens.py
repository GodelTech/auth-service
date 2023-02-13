import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.business_logic.services import TokenService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    GrantNotFoundError,
    WrongGrantsError,
)
from src.di.providers import provide_token_service_stub
from src.presentation.api.models.tokens import (
    BodyRequestTokenModel,
    ResponseTokenModel,
)

logger = logging.getLogger(__name__)


token_router = APIRouter(
    prefix="/token",
)


@token_router.post("/", response_model=ResponseTokenModel, tags=["Token"])
async def get_tokens(
    request: Request,
    request_body: BodyRequestTokenModel = Depends(),
    token_class: TokenService = Depends(provide_token_service_stub),
):
    try:
        token_class = token_class
        token_class.request = request
        token_class.request_model = request_body
        result = await token_class.get_tokens()
        return result

    except ClientNotFoundError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this",
        )
    except WrongGrantsError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token"
        )

    except GrantNotFoundError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token"
        )

    except ValueError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all required parameters were send",
        )
