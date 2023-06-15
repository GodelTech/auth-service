from __future__ import annotations
from src.business_logic.get_tokens.factory import TokenServiceFactory
from src.business_logic.jwt_manager import JWTManager
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
    DeviceRepository,
    BlacklistedTokenRepository,
    CodeChallengeRepository
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def provide_token_service_factory(db_session: AsyncSession) -> TokenServiceFactory:
    return TokenServiceFactory(
        session=db_session,
        client_repo=ClientRepository(session=db_session),
        persistent_grant_repo=PersistentGrantRepository(session=db_session),
        user_repo=UserRepository(session=db_session),
        device_repo=DeviceRepository(session=db_session),
        code_challenge_repo=CodeChallengeRepository(session=db_session),
        jwt_manager=JWTManager(),
        blacklisted_repo=BlacklistedTokenRepository(session=db_session)
    )
