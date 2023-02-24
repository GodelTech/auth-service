from src.business_logic.dependencies.database import get_repository_no_depends
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from typing import Any, Optional

class UserInfoServices:
    def __init__(
            self,
            jwt: JWTService,
            user_repo: UserRepository,
            client_repo: ClientRepository,
            persistent_grant_repo: PersistentGrantRepository,
    ) -> None:
        self.jwt = jwt
        self.authorization: Optional[str] = None
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo


    async def get_user_info(
        self,
    ) -> dict[str, Any]:
        
        if self.authorization is None:
            raise ValueError
        
        token = self.authorization
        try:
            decoded_token = await self.jwt.decode_token(token=token)
            sub = int(decoded_token["sub"])
        except:
            raise ValueError

        claims_dict = await self.user_repo.get_claims(id=sub)
        response = {"sub": str(sub)} | claims_dict

        return response

    async def get_user_info_jwt(self) -> str:
        result = await self.get_user_info()
        token = await self.jwt.encode_jwt(payload=result)
        return token
