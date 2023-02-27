import logging
from typing import Optional, Union

from src.business_logic.dto import AdminCredentialsDTO
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.repositories import UserRepository

logger = logging.getLogger(__name__)


class AdminAuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordHash,
        jwt_service: JWTService,
    ) -> None:
        self.user_repo = user_repo
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def authorize(
        self, credentials: AdminCredentialsDTO
    ) -> Union[str, None]:
        user_hash_password, user_id = await self.user_repo.get_hash_password(
            credentials.username
        )
        if self.password_service.validate_password(
            credentials.password, user_hash_password
        ):
            # TODO: Implement admin token generation.
            return "Test Token"
        return None

    async def authenticate(self, token: str) -> bool:
        if token is None:
            return False

        return True
