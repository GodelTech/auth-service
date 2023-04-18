import datetime
from typing import Any, Dict, Optional

from fastapi import Request
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.presentation.api.models.introspection import (
    BodyRequestIntrospectionModel,
)


class IntrospectionService:
    KEYS_TO_EXTRACT = [
        "username",
        "exp",
        "iat",
        "client_id",
        "jti",
        "aud",
        "nbf",
        "scope",
    ]

    def __init__(
        self,
        jwt: JWTService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
    ) -> None:
        self.jwt = jwt
        self.request: Optional[Request] = None
        self.authorization: Optional[str] = None
        self.request_body: Optional[BodyRequestIntrospectionModel] = None
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.key_operations = {"username": self.get_username_by_id}

    async def analyze_token(self) -> Dict[str, Any]:
        if self.request_body is None:
            raise ValueError
        decoded_token = {}
        response: Dict[str, Any] = {}
        try:
            decoded_token = await self.jwt.decode_token(
                token=self.request_body.token, audience="introspection"
            )
        except ExpiredSignatureError:
            return {"active": False}
        except PyJWTError:
            raise ValueError
        else:
            if self.request_body.token_type_hint in (
                "access-token",
                "access_token",
                "access",
            ):
                response["active"] = True

        if response == {}:
            if self.request_body.token_type_hint is None:
                list_of_types = [
                    token_type[0]
                    for token_type in await self.persistent_grant_repo.get_all_types()
                ]

                for token_type in list_of_types:
                    if await self.persistent_grant_repo.exists(
                        grant_type=token_type,
                        grant_data=self.request_body.token,
                    ):
                        self.request_body.token_type_hint = token_type
                        response = {"active": True}
                        break
            else:
                exists = await self.persistent_grant_repo.exists(
                    grant_type=self.request_body.token_type_hint,
                    grant_data=self.request_body.token,
                )
                response = {"active": exists}

        if response["active"]:
            response["sub"] = decoded_token["sub"]
            response["iss"] = self.slice_url()
            response["token_type"] = self.get_token_type()

            for key in self.KEYS_TO_EXTRACT:
                try:
                    if key in self.key_operations:
                        response[key] = await self.key_operations[key](
                            decoded_token["sub"]
                        )
                    elif key in decoded_token:
                        response[key] = decoded_token[key]
                except:
                    pass
            # try:
            #     response["username"] = await self.user_repo.get_username_by_id(
            #         id=int(decoded_token["sub"])
            #     )
            # except:
            #     pass

            # try:
            #     response["exp"] = decoded_token["exp"]
            # except:
            #     pass

            # try:
            #     response["iat"] = decoded_token["iat"]
            # except:
            #     pass

            # try:
            #     response["client_id"] = decoded_token["client_id"]
            # except:
            #     pass

            # for claim in (
            #     "jti",
            #     "aud",
            #     "nbf",
            #     "scope",
            # ):
            #     if claim in decoded_token.keys():
            #         response[claim] = decoded_token[claim]

        return response

    async def get_client_id(self) -> str:
        if self.request_body is None:
            raise ValueError
        grant = await self.persistent_grant_repo.get(
            grant_data=self.request_body.token,
            grant_type=self.request_body.token_type_hint,
        )
        return grant.client_id

    def get_token_type(self) -> str:
        return "Bearer"

    def slice_url(self) -> str:
        if self.request is None:
            raise ValueError
        result = str(self.request.url).rsplit("/", 2)
        return result[0]

    def time_diff_in_seconds(
        self,
        finish: datetime.datetime = datetime.datetime.now(),
        start: datetime.datetime = datetime.datetime(1970, 1, 1),
    ) -> int:
        return int((finish - start).total_seconds())

    async def get_username_by_id(self, id: int) -> str:
        return await self.user_repo.get_username_by_id(id=id)
