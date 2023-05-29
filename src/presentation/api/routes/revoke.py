import logging
from typing import Union

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories import (
    PersistentGrantRepository,
    ClientRepository,
    UserRepository,
    DeviceRepository,
    BlacklistedTokenRepository,
)
from src.presentation.api.models.revoke import BodyRequestRevokeModel
from src.presentation.middleware.authorization_validation import (
    authorization_middleware,
)
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

revoke_router = APIRouter(
    prefix="/revoke",
    tags=["Revoke"],
    dependencies=[Depends(authorization_middleware)],
)


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
    session: AsyncSession = Depends(provide_async_session_stub)
) -> None:
    session = session
    token_class = TokenService(
        session=session,
        client_repo=ClientRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        user_repo=UserRepository(session),
        device_repo=DeviceRepository(session),
        blacklisted_repo=BlacklistedTokenRepository(session),
        jwt_service=JWTService(),
    )
    token_class.request = request
    token_class.request_body = request_body
    token = request.headers.get("authorization") or auth_swagger
    token_class.authorization = token
    logger.info(f"Revoking for token {request_body.token} started")
    revoke_token = await token_class.revoke_token()
    await session.commit()
    return revoke_token
