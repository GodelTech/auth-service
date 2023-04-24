import logging
from typing import Optional, Union
import time 
from src.business_logic.dto import AdminCredentialsDTO
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import UserRepository, PersistentGrantRepository

logger = logging.getLogger(__name__)


class AdminAuthService:
    def __init__(
        self,
        uow, 
        password_service = PasswordHash,
        jwt_service = JWTService
    ) -> None:
        self.uow = uow
        
        self.password_service = password_service
        self.jwt_service = jwt_service

    async def authorize(
        self, credentials: AdminCredentialsDTO, exp_time: int = 900
    ) -> Union[str, None]:
        async with self.uow as session:
            user_repo = UserRepository(session)
            user_hash_password, user_id = await user_repo.get_hash_password(
                credentials.username
            )
        self.password_service.validate_password(
            credentials.password, 
            user_hash_password
        )
        return await self.jwt_service.encode_jwt(
            payload={
                "sub":user_id,
                "exp": exp_time + int(time.time()),
                "aud":["admin","introspection", "revoke"]
            }
        )
    

    async def authenticate(self, token: str) -> bool:
        return await self.jwt_service.verify_token(token=token, aud="admin")
        
