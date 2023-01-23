import datetime

from jwt.exceptions import ExpiredSignatureError

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.business_logic.dependencies.database import get_repository_no_depends


class IntrospectionServies:
    def __init__(
        self,
        jwt: JWTService,
        # token_service: TokenService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self.jwt = jwt
        self.request = ...
        self.authorization = ...
        self.request_body = ...
        # self.token_service = token_service
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo

    async def analyze_token(self) -> dict:
        decoded_token = {}

        try:
            decoded_token = await self.jwt.decode_token(token=self.request_body.token)
        except ExpiredSignatureError:
            return {"active": False}
        except:
            raise ValueError
        
        response = {}

        if self.request_body.token_type_hint is None:

            list_of_types = [token_type[0] for token_type in PersistentGrant.TYPES_OF_GRANTS]
            
            for token_type in list_of_types:
                if await self.persistent_grant_repo.exists(grant_type = token_type, data=self.request_body.token):
                    self.request_body.token_type_hint = token_type
                    response = {"active": True}
                    break
        else:
            exists = await self.persistent_grant_repo.exists(grant_type = self.request_body.token_type_hint, data=self.request_body.token)
            response = {"active": exists}
        
        if response["active"]:
            response["sub"] = decoded_token["sub"]
            response["iss"] = self.slice_url()
            response["token_type"] = self.get_token_type()
            
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
                response['client_id'] = await self.get_client_id()
            except:
                pass

            for claim in ('jti', 'aud', 'nbf', 'scope',):
                if claim in decoded_token.keys():
                    response[claim] = decoded_token[claim]

        return response

    async def get_client_id(self) -> str:
        grant = await self.persistent_grant_repo.get(data=self.request_body.token, grant_type=self.request_body.token_type_hint)
        return grant.client_id

    def get_token_type(self) -> str:
        return 'Bearer'

    def slice_url(self) -> str:
        result = str(self.request.url).rsplit('/', 2)
        return result[0]

    def time_diff_in_seconds(self, finish: datetime.datetime = datetime.datetime.now(), start: datetime.datetime = datetime.datetime(1970, 1, 1)) -> int:
        return int((finish - start).total_seconds())
