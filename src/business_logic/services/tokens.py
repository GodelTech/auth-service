import logging
import time

from typing import Union

from src.business_logic.dependencies.database import get_repository_no_depends
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors import WrongGrantsError
from src.data_access.postgresql.errors import GrantNotFoundError
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository
)


logger = logging.getLogger("is_app")


def get_base_payload(user_id: str, client_id: str, expiration_time: int) -> dict:
    base_payload = {
        'iss': 'http://localhost:8000',
        'sub': user_id,
        'client': client_id,
        'iat': int(time.time()),
        'exp': int(time.time() + expiration_time)
    }
    return base_payload


async def get_single_token(
    user_id: str, 
    client_id: str, 
    additional_data: dict, 
    jwt_service: JWTService, 
    expiration_time: int
    ) -> str:
    """
    It can be used for id, access and refresh token.
    'Additional data' means scopes for access/refresh token and claims for id token
    """
    base_payload = get_base_payload(user_id=user_id, client_id=client_id, expiration_time=expiration_time)
    full_payload = {**base_payload, **additional_data}
    access_token = await jwt_service.encode_jwt(payload=full_payload)
    return access_token


class TokenService:
    def __init__(
            self,
            client_repo: ClientRepository,
            persistent_grant_repo: PersistentGrantRepository,
            user_repo: UserRepository,
            jwt_service: JWTService
    ) -> None:
        self.request_model = ...
        self.authorization = ...
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.user_repo = user_repo
        self.jwt_service = jwt_service

    async def get_tokens(self) -> dict:
        if self.request_model.grant_type == "code" \
                and (self.request_model.redirect_uri is None or self.request_model.code is None):
            raise ValueError

        elif self.request_model.grant_type == "password" and (
            self.request_model.username is None
            or self.request_model.password is None
        ):
            raise ValueError
        elif (
            self.request_model.grant_type == "refresh_token"
            and self.request_model.refresh_token is None
        ):
            raise ValueError

        elif (
            self.request_model.grant_type
            == "urn:ietf:params:oauth:grant-type:device_code"
            and self.request_model.device_code is None
        ):
            raise ValueError

        if await self.client_repo.get_client_by_client_id(
            client_id=self.request_model.client_id
        ):
            expiration_time = 600
            if self.request_model.grant_type == "code":
                if await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    data=self.request_model.code,
                ):
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
                    client_id = self.request_model.client_id

                    # ACCESS TOKEN
                    scopes = {"scopes": self.request_model.scope}
                    access_token = await get_single_token(
                        user_id,
                        client_id, 
                        additional_data=scopes, 
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time
                        )

                    # ID TOKEN
                    claims = await self.user_repo.get_claims(id=1)
                    id_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=claims,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time
                    )

                    # deleting old grant because now it won't be used anywhere aand...
                    await self.persistent_grant_repo.delete(
                        data=self.request_model.code,
                        grant_type=self.request_model.grant_type,
                    )

                    # ...creating new refresh token grant
                    refresh_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=scopes,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time*6
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
                        "token_type": "Bearer",
                    }

            if self.request_model.grant_type == "refresh_token":

                refresh_token = self.request_model.refresh_token
                if await self.persistent_grant_repo.exists(
                    grant_type="refresh_token", data=refresh_token
                ):
                    grant = await self.persistent_grant_repo.get(
                        grant_type="refresh_token",
                        data=refresh_token,
                    )

                    user_id = grant.subject_id
                    client_id = self.request_model.client_id

                    decoded = await self.jwt_service.decode_token(refresh_token)
                    old_expiration = decoded['exp']

                    if old_expiration < time.time():
                        # If token expired
                        await self.persistent_grant_repo.delete(
                            data=refresh_token,
                            grant_type=self.request_model.grant_type,
                        )

                        # REFRESH TOKEN
                        scopes = {"scopes": self.request_model.scope}
                        new_refresh_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=scopes,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time*6
                        )

                        await self.persistent_grant_repo.create(
                            client_id=client_id,
                            data=new_refresh_token,
                            expiration_time=expiration_time,
                            user_id=user_id,
                            grant_type="refresh_token",
                        )

                        # ACCESS TOKEN
                        access_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=scopes,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time
                        )


                        # ID TOKEN
                        claims = await self.user_repo.get_claims(user_id)
                        id_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=claims,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time
                        )

                        response = {
                            "access_token": access_token,
                            "token_type": "Bearer",
                            "refresh_token": new_refresh_token,
                            "expires_in": expiration_time,
                            "id_token": id_token,
                        }

                        return response
                    else:
                        # if token didn't expired
                        # ACCESS TOKEN
                        scopes = {'scope': self.request_model.scope}
                        new_access_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=scopes,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time*6
                        )

                        # ID TOKEN
                        claims = await self.user_repo.get_claims(user_id)
                        id_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=claims,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time
                        )
                        response = {
                            "access_token": new_access_token,
                            "token_type": "Bearer",
                            "refresh_token": self.request_model.refresh_token,
                            "expires_in": expiration_time,
                            "id_token": id_token,
                        }

                        return response

    async def revoke_token(self):

        token_type_hint = self.request_body.token_type_hint
        if token_type_hint == 'refresh_token':
            logger.info('I am here')
            logger.info(f'{token_type_hint}')
            logger.info(f'{self.request_body.token}')
            if await self.persistent_grant_repo.exists(grant_type=token_type_hint, data=self.request_body.token):
                await self.persistent_grant_repo.delete(
                    grant_type=token_type_hint, 
                    data=self.request_body.token
                )
            else:
                raise GrantNotFoundError
        elif token_type_hint == 'access_token':
            # TODO: realize logic for access_token revocation.
            pass
        else:
            raise GrantNotFoundError
