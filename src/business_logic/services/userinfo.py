from fastapi import Depends

from src.business_logic.dependencies.database import get_repository
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.user import UserRepository


class UserInfoServies:
    def __init__(
        self,
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
    ) -> None:
        self.jwt = JWTService()
        #self.token_service = TokenService()
        self.authorization = ...
        self.user_repo = user_repo

    async def get_user_info(
        self,
    ) -> dict:
        token = self.authorization

        #await self.token_service.checheck_authorisation_token(token = token)
        try:
            sub = int(self.jwt.decode_token(token=token)["sub"])
        except:
            raise ValueError

        claims_dict = await self.user_repo.get_claims(id=sub)
        response = {"sub": str(sub)} | claims_dict

        return response

    async def get_user_info_jwt(self) -> str:
        result = await self.get_user_info()
        return self.jwt.encode_jwt(payload=result, include_expire=False)
