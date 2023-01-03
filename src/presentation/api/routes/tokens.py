import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.business_logic.services import TokenService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    WrongGrantsError,
)
from src.presentation.api.models.tokens import (
    BodyRequestTokenModel,
    ResponseTokenModel,
)

logger = logging.getLogger("is_app")


token_router = APIRouter(
    prefix="/token",
)


@token_router.post("/", response_model=ResponseTokenModel, tags=["Token"])
async def get_tokens(
    request_body: BodyRequestTokenModel = Depends(),
    token_class: TokenService = Depends(),
):
    try:
        token_class = token_class
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
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all required parameters were send",
        )
