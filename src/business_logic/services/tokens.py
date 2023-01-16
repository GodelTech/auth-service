import logging

from fastapi import Depends

from src.business_logic.dependencies.database import get_repository
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors import WrongGrantsError
from src.data_access.postgresql.errors import GrantNotFoundError
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
)
from src.presentation.api.models import BodyRequestTokenModel


logger = logging.getLogger("is_app")


class TokenService:
    def __init__(
        self,
        # request_model: BodyRequestTokenModel,
        client_repo: ClientRepository = Depends(
            get_repository(ClientRepository)
        ),
        persistent_grant_repo: PersistentGrantRepository = Depends(
            get_repository(PersistentGrantRepository)
        ),
    ) -> None:
        self.request_model = ...
        self.authorization = ...
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.jwt_service = JWTService()

    async def get_tokens(self) -> list:

        if self.request_model.grant_type == "authorization_code" and (
            self.request_model.redirect_uri == None
            or self.request_model.code == None
        ):
            raise ValueError

        elif self.request_model.grant_type == "password" and (
            self.request_model.username == None
            or self.request_model.password == None
        ):
            raise ValueError

        elif (
            self.request_model.grant_type == "refresh_token"
            and self.request_model.refresh_token == None
        ):
            raise ValueError

        elif (
            self.request_model.grant_type
            == "urn:ietf:params:oauth:grant-type:device_code"
            and self.request_model.device_code == None
        ):
            raise ValueError

        if await self.client_repo.get_client_by_client_id(
            client_id=self.request_model.client_id
        ):
            if await self.persistent_grant_repo.exists(
                grant_type=self.request_model.grant_type,
                data=self.request_model.code,
            ):
                if self.request_model.grant_type == "code":
                    grant = await self.persistent_grant_repo.get(
                        grant_type=self.request_model.grant_type,
                        data=self.request_model.code,
                    )

                    # checks if client provided in request is the same that in the db have provided grants
                    if grant.client_id != self.request_model.client_id:
                        raise WrongGrantsError(
                            "Client from request has been found in the database\
                            but don't have provided grants"
                        )

                    user_id = grant.subject_id
                    access_token = self.jwt_service.encode_jwt(
                        payload={"sub": str(user_id)}, include_expire=False
                    )

                    expiration_time = 600
                    self.jwt_service.set_expire_time(
                        expire_seconds=expiration_time
                    )
                    refresh_token = self.jwt_service.encode_jwt(
                        payload={"sub": str(user_id)}, include_expire=True
                    )

                    id_token = self.jwt_service.encode_jwt(
                        payload={"sub": str(user_id)}, include_expire=False
                    )
                    token_type = "Bearer"

                    # deleting old grant because now it won't be used anywhere aand...
                    await self.persistent_grant_repo.delete(
                        client_id=self.request_model.client_id,
                        data=self.request_model.code,
                        grant_type=self.request_model.grant_type,
                    )

                    # creating new refresh token grant
                    self.jwt_service.set_expire_time(
                        expire_seconds=expiration_time
                    )
                    refresh_token = self.jwt_service.encode_jwt(
                        {"user_id": str(user_id)}, include_expire=True
                    )

                    await self.persistent_grant_repo.create(
                        client_id=self.request_model.client_id,
                        data=refresh_token,
                        expiration_time=expiration_time,
                        user_id=user_id,
                        grant_type="refresh_token",
                    )

                    return {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "id_token": id_token,
                        "expires_in": expiration_time,
                        "token_type": token_type,
                    }

                if self.request_model.grant_type == "refresh_token":

                    refresh_token = self.request_model.refresh_token
                    if await self.persistent_grant_repo.exists(
                        grant_type="refresh_token", data=refresh_token
                    ):
                        if not self.jwt_service.check_spoiled_token(
                            refresh_token
                        ):

                            grant = await self.persistent_grant_repo.get(
                                grant_type=self.request_model.grant_type,
                                data=self.request_model.refresh_token,
                            )
                            user_id = grant.subject_id

                            await self.persistent_grant_repo.delete(
                                client_id=self.request_model.client_id,
                                data=self.request_model.refresh_token,
                                grant_type=self.request_model.grant_type,
                            )

                            expiration_time = 600
                            self.jwt_service.set_expire_time(
                                expire_seconds=expiration_time
                            )
                            refresh_token = self.jwt_service.encode_jwt(
                                {"sub": str(user_id)}, include_expire=True
                            )

                            await self.persistent_grant_repo.create(
                                client_id=self.request_model.client_id,
                                data=refresh_token,
                                expiration_time=expiration_time,
                                user_id=user_id,
                                grant_type="refresh_token",
                            )

                            access_token = self.jwt_service.encode_jwt(
                                {"sub": str(user_id)}, include_expire=False
                            )
                            id_token = self.jwt_service.encode_jwt(
                                {"sub": str(user_id)}, include_expire=False
                            )

                            response = {
                                "access_token": access_token,
                                "token_type": "Bearer",
                                "refresh_token": refresh_token,
                                "expires_in": expiration_time,
                                "id_token": id_token,
                            }

                            return response
                        else:
                            access_token = self.jwt_service.encode_jwt(
                                {"sub": str(user_id)}, include_expire=False
                            )

                            return {"access_token": access_token}

    async def revoke_token(self):

        await self.check_authorisation_token(token = self.authorization)
    
        if self.request_body.token_type_hint != None:
            type_list = {self.request_body.token_type_hint, }
        else:
            type_list = {"access_token", "refresh_token"}

        for token_type in type_list:
            if await self.persistent_grant_repo.exists(grant_type=token_type, data=self.request_body.token):
                self.persistent_grant_repo.delete(
                    grant_type=token_type, data=self.request_body.token)
                break
        else:
            raise GrantNotFoundError

    async def check_authorisation_token(self, secret: str, token: str, token_type_hint: str = "access_token") -> Exception | bool:
        """ 
        Returns True if authorisation token is correct.
        Else rises PermissionError.
        token_type_hint default value is 'access_token'.
        """

        if await self.jwt_service.check_spoiled_token(secret=secret, token=token):
            raise PermissionError
        elif not await self.persistent_grant_repo.exists(grant_type=token_type_hint, data=token):
            raise PermissionError
        else:
            return True
