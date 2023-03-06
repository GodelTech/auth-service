import logging
from typing import Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from src.business_logic.services import JWTService, TokenService
from src.data_access.postgresql.errors import GrantNotFoundError
from src.di.providers import provide_token_service_stub
from src.presentation.api.models.revoke import BodyRequestRevokeModel

logger = logging.getLogger(__name__)

revoke_router = APIRouter(prefix="/revoke", tags=["Revoke"])


@revoke_router.post(
    "/",
    status_code=200,
)
async def post_revoke_token(
    request: Request,
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    request_body: BodyRequestRevokeModel = Depends(),
    token_class: TokenService = Depends(provide_token_service_stub),
) -> None:
    try:
        token_class = token_class
        token_class.request = request
        token_class.request_body = request_body
        token = request.headers.get("authorization") or auth_swagger
        token_class.authorization = token
        logger.info(f"Revoking for token {request_body.token} started")
        return await token_class.revoke_token()

    except GrantNotFoundError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token"
        )


@revoke_router.get("/test_token", status_code=200)
async def get_test_token(request: Request) -> str:
    return await JWTService().encode_jwt(payload={"sub": "1"})
