from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from fastapi import Depends
from src.business_logic.dependencies.database import get_repository
import datetime


class IntrospectionServies():
    def __init__(self,
                 grant_repo: PersistentGrantRepository = Depends(
                     get_repository(PersistentGrantRepository)),
                 user_repo: UserRepository = Depends(
                     get_repository(UserRepository)),
                 client_repo: UserRepository = Depends(
                     get_repository(ClientRepository))
                 ) -> None:
        self.jwt = JWTService()
        self.request = ...
        self.request_headers = ...
        self.request_body = ...
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = grant_repo

    async def analyze_token(self) -> dict:

        if not await self.authorization_check():
            raise ValueError

        decoded_token = self.jwt.decode_token(token=self.request_body.token)
        
        response = {}

        if self.request_body.token_type_hint == None:

            list_of_types = [token_type[0] for token_type in PersistentGrant.TYPES_OF_GRANTS]
            
            for token_type in list_of_types:
                if await self.persistent_grant_repo.exists(grant_type = token_type, data=decoded_token["data"]):
                    if not self.jwt.check_spoiled_token(token=self.request_body.token):
                        self.request_body.token_type_hint = token_type
                        response = {"active": not self.jwt.check_spoiled_token(token=self.request_body.token)}
                        break
        else:
            exists = self.persistent_grant_repo.exists(grant_type = self.request_body.token_type_hint, data=decoded_token["data"])
            spoiled = self.jwt.check_spoiled_token(token=self.request_body.token)
            response = {"active": exists and not spoiled}
        
        if response["active"]:
            response["sub"] = decoded_token["sub"]

            try:
                response["username"] = await self.user_repo.get_username_by_id(id=int(decoded_token["sub"]))
            except:
                pass

            try:
                response["exp"] = datetime.datetime.strptime(decoded_token["expire"], '%Y-%m-%d %H:%M:%S').timestamp()
            except:
                pass

            try:
                response["iat"] = decoded_token["token_issued"]
            except:
                pass

            try:
                response["iss"] = self.slice_url()
            except:
                pass

            try:
                response["token_type"] = self.get_token_type()
            except:
                pass

            for claim in ('jti', 'aud', 'nbf', 'scope', 'client_id'):
                if claim in decoded_token.keys():
                    response[claim] = decoded_token[claim]

        return response

    def get_token_type(self) -> str:
        return 'Bearer'

    def slice_url(self) -> str:
        result = str(self.request.url).rsplit('/', 2)
        return result[0]

    async def authorization_check(self) -> bool:
        decoded_token = self.jwt.decode_token(
            token=self.request_headers.authorization)
        exists = await self.persistent_grant_repo.exists(grant_type="access_token", data=decoded_token["data"])
        spoiled = self.jwt.check_spoiled_token(
            token=self.request_headers.authorization)
        return exists and not spoiled

    def time_diff_in_seconds(self, finish: datetime.datetime = datetime.datetime.now(), start: datetime.datetime = datetime.datetime(1970, 1, 1)) -> int:
        return int((finish - start).total_seconds())
