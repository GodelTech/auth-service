import logging
from typing import Optional, Union
import time 
from src.business_logic.dto import AdminCredentialsDTO
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories import UserRepository, PersistentGrantRepository
from src.data_access.postgresql.errors import UserNotInGroupError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from src.dyna_config import DOMAIN_NAME

logger = logging.getLogger(__name__)


class AdminAuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        password_service = PasswordHash(),
        jwt_service = JWTService(),
    ) -> None:
        self.user_repo = user_repo
        self.password_service = password_service
        self.jwt_service = jwt_service
    
    async def authorize(
        self, credentials: AdminCredentialsDTO, exp_time: int = 900
    ) -> Union[str, None]:
        user_hash_password, user_id = await self.user_repo.get_hash_password(
            credentials.username
        )
        self.password_service.validate_password(
            credentials.password, 
            user_hash_password
        )
        if not await self.user_repo.check_user_group(username=credentials.username, groupname='administration'):
            raise UserNotInGroupError('administration')
        return await self.jwt_service.encode_jwt(
            payload={
                "sub":user_id,
                "exp": exp_time + int(time.time()),
                "aud":["admin"]
            }
        )
    

    async def authenticate(self, token: str) -> Union[None, RedirectResponse]:
        if await self.jwt_service.verify_token(token=token, aud="admin"):
            return None
        else:
            # return None
            return RedirectResponse(f"/admin/login")
        
