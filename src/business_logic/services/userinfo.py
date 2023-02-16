from typing import Any, Dict, Optional

from src.business_logic.dependencies.database import get_repository_no_depends
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories.user import UserRepository


class UserInfoServices:
    def __init__(
        self,
        jwt: JWTService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
    ) -> None:
        self.jwt = jwt
        self.authorization = ...
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.client_id = None
        self.secret = None

    async def get_user_info(
        self,
    ) -> Optional[Dict[str, Any]]:
        if self.authorization is not Ellipsis:
            token = self.authorization
            try:
                decoded_token = await self.jwt.decode_token(token=token)
                sub = int(decoded_token["sub"])
            except:
                raise ValueError

            claims_dict = await self.user_repo.get_claims(id=sub)
            response = {"sub": str(sub)} | claims_dict

            return response
        return None

    async def get_user_info_jwt(self) -> Optional[str]:
        result = await self.get_user_info()
        if result is not None:
            token = await self.jwt.encode_jwt(payload=result)
            return token
        return None
