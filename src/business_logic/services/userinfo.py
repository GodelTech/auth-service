from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.user import UserRepository
from fastapi import Depends
from src.business_logic.dependencies.database import get_repository

class UserInfoServies():
    def __init__(self, user_repo:UserRepository = Depends(get_repository(UserRepository))) -> None:
        self.jwt = JWTService()
        self.request = ...
        self.user_repo = user_repo

    async def get_user_info(self,) -> dict:
        token=self.request.authorization
        
        if self.jwt.check_spoiled_token(token = token):
            raise ValueError

        sub = int(self.jwt.decode_token(token = token)['sub'])
        claims_dict = await self.user_repo.get_claims(id=sub)
        response = {"sub": str(sub)} | claims_dict

        return response

    async def get_user_info_jwt(self) -> str:
        result = await self.get_user_info()
        return  self.jwt.encode_jwt(result)