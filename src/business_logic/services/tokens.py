import datetime
import logging
import time
import uuid
from typing import Union

from src.business_logic.dependencies.database import get_repository_no_depends
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    GrantNotFoundError,
    WrongGrantsError,
    DeviceRegistrationError,
    DeviceCodeNotFoundError,
    DeviceCodeExpirationTimeError,
)
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
    DeviceRepository,
)
from src.presentation.api.models import BodyRequestTokenModel

logger = logging.getLogger(__name__)


def get_base_payload(client_id: str, expiration_time: int, **kwargs) -> dict:

    if kwargs.get("user_id") and kwargs["user_id"] != "":
        kwargs["sub"] = kwargs.get("user_id")

    if kwargs.get("user_id"):
        kwargs.pop("user_id")

    base_payload = {
        "iss": "http://localhost:8000",
        "client_id": client_id,
        "iat": int(time.time()),
        "exp": int(time.time() + expiration_time),
    } | kwargs
    return base_payload


async def get_single_token(
    client_id: str,
    additional_data: dict,
    jwt_service: JWTService,
    expiration_time: int,
    **kwargs,
) -> str:
    """
    It can be used for id, access and refresh token.
    'Additional data' means scopes for access/refresh token and claims for id token
    """
    base_payload = get_base_payload(
        # user_id=user_id,
        client_id=client_id,
        expiration_time=expiration_time,
        **kwargs,
    )
    full_payload = {**base_payload, **additional_data}
    access_token = await jwt_service.encode_jwt(payload=full_payload)
    return access_token


class TokenService:
    def __init__(
        self,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
        device_repo: DeviceRepository,
        jwt_service: JWTService,
    ) -> None:
        self.request = ...
        self.request_model = ...
        self.authorization = ...
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.jwt_service = jwt_service

    async def get_tokens(self) -> dict:
        if self.request_model.grant_type == "code" and (
            self.request_model.redirect_uri is None
            or self.request_model.code is None
        ):
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

        elif self.request_model.grant_type == "client_credentials":
            if self.request_model.client_secret is None:
                raise ValueError
            return await self.get_client_credentials()

        if bool(
            await self.client_repo.get_client_by_client_id(
                client_id=self.request_model.client_id
            )
        ):
            expiration_time = 600
            if self.request_model.grant_type == "code":
                if await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    grant_data=self.request_model.code,
                ):
                    grant = await self.persistent_grant_repo.get(
                        grant_type=self.request_model.grant_type,
                        grant_data=self.request_model.code,
                    )

                    # checks if client provided in request is the same that in the db have provided grants
                    if grant.client.client_id != self.request_model.client_id:
                        raise WrongGrantsError(
                            "Client from request has been found in the database\
                            but don't have provided grants"
                        )
                    user_id = grant.user_id
                    client_id = self.request_model.client_id

                    # ACCESS TOKEN
                    scopes = {"scopes": self.request_model.scope}
                    access_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=scopes,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time,
                    )

                    # ID TOKEN
                    claims = await self.user_repo.get_claims(id=1)
                    id_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=claims,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time,
                    )

                    # deleting old grant because now it won't be used anywhere aand...
                    await self.persistent_grant_repo.delete(
                        grant_data=self.request_model.code,
                        grant_type=self.request_model.grant_type,
                    )

                    # ...creating new refresh token grant
                    refresh_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=scopes,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time * 6,
                    )

                    await self.persistent_grant_repo.create(
                        client_id=self.request_model.client_id,
                        grant_data=refresh_token,
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

                else:
                    raise GrantNotFoundError

            if self.request_model.grant_type == "refresh_token":

                refresh_token = self.request_model.refresh_token
                if await self.persistent_grant_repo.exists(
                    grant_type="refresh_token", grant_data=refresh_token
                ):
                    grant = await self.persistent_grant_repo.get(
                        grant_type="refresh_token",
                        grant_data=refresh_token,
                    )

                    user_id = grant.user_id
                    client_id = self.request_model.client_id

                    decoded = await self.jwt_service.decode_token(refresh_token)
                    old_expiration = decoded["exp"]

                    if old_expiration < time.time():
                        # If token expired
                        await self.persistent_grant_repo.delete(
                            grant_data=refresh_token,
                            grant_type=self.request_model.grant_type,
                        )

                        # REFRESH TOKEN
                        scopes = {"scopes": self.request_model.scope}
                        new_refresh_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=scopes,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time * 6,
                        )

                        await self.persistent_grant_repo.create(
                            client_id=client_id,
                            grant_data=new_refresh_token,
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
                            expiration_time=expiration_time,
                        )

                        # ID TOKEN
                        claims = await self.user_repo.get_claims(user_id)
                        id_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=claims,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time,
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
                        scopes = {"scope": self.request_model.scope}
                        new_access_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=scopes,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time * 6,
                        )

                        # ID TOKEN
                        claims = await self.user_repo.get_claims(user_id)
                        id_token = await get_single_token(
                            user_id=user_id,
                            client_id=client_id,
                            additional_data=claims,
                            jwt_service=self.jwt_service,
                            expiration_time=expiration_time,
                        )
                        response = {
                            "access_token": new_access_token,
                            "token_type": "Bearer",
                            "refresh_token": self.request_model.refresh_token,
                            "expires_in": expiration_time,
                            "id_token": id_token,
                        }

                        return response
                else:
                    raise GrantNotFoundError

            if self.request_model.grant_type == "urn:ietf:params:oauth:grant-type:device_code":
                if not await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    grant_data=self.request_model.device_code,
                ):
                    if await self.device_repo.validate_device_code(device_code=self.request_model.device_code):
                        # add check for expire time
                        now = datetime.datetime.now()
                        check_time = datetime.datetime.timestamp(now)
                        expire_in = await self.device_repo.get_expiration_time(device_code=self.request_model.device_code)
                        if check_time > expire_in:
                            await self.device_repo.delete_by_device_code(device_code=self.request_model.device_code)
                            raise DeviceCodeExpirationTimeError("Device code expired")
                        raise DeviceRegistrationError("Device registration in progress")
                    else:
                        raise DeviceCodeNotFoundError("Such device code does not exist")
                elif await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    grant_data=self.request_model.device_code,
                ):
                    grant = await self.persistent_grant_repo.get(
                        grant_type=self.request_model.grant_type,
                        grant_data=self.request_model.device_code,
                    )

                    # checks if client provided in request is the same that in the db have provided grants
                    if grant.client.client_id != self.request_model.client_id:
                        raise WrongGrantsError(
                            "Client from request has been found in the database\
                            but don't have provided grants"
                        )
                    user_id = grant.user_id
                    client_id = self.request_model.client_id

                    # ACCESS TOKEN
                    scopes = {"scopes": self.request_model.scope}
                    access_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=scopes,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time,
                    )

                    # deleting old grant because now it won't be used anywhere and...
                    await self.persistent_grant_repo.delete(
                        grant_data=self.request_model.device_code,
                        grant_type=self.request_model.grant_type,
                    )

                    # ...creating new refresh token grant
                    refresh_token = await get_single_token(
                        user_id=user_id,
                        client_id=client_id,
                        additional_data=scopes,
                        jwt_service=self.jwt_service,
                        expiration_time=expiration_time * 6,
                    )

                    await self.persistent_grant_repo.create(
                        client_id=self.request_model.client_id,
                        grant_data=refresh_token,
                        expiration_time=expiration_time,
                        user_id=user_id,
                        grant_type="refresh_token",
                    )
                    return {
                        "access_token": access_token,
                        "token_type": "Bearer",
                        "expires_in": expiration_time,
                        "refresh_token": refresh_token,
                    }

                else:
                    raise GrantNotFoundError

    async def get_client_credentials(self) -> dict:
        expiration_time = 600
        client_from_db = ...

        try:
            client_from_db = await self.client_repo.get_client_by_client_id(
                client_id=self.request_model.client_id
            )
            if not bool(client_from_db):
                raise ClientNotFoundError

            if (
                await self.client_repo.get_client_secrete_by_client_id(
                    client_id=self.request_model.client_id
                )
                != self.request_model.client_secret
            ):
                raise ClientNotFoundError
        except:
            raise ClientNotFoundError

        scopes = await self.client_repo.get_client_scopes(
            client_id=client_from_db.id
        )
        if len(scopes) == 1:
            scopes = scopes[0]
        elif len(scopes) == 0:
            scopes = "No scope"

        audience = await self.client_repo.get_client_claims(
            client_id=client_from_db.id
        )
        access_token = await self.jwt_service.encode_jwt(
            {
                # "arc" : client_from_db.arc,
                # # ACR value is a set of arbitrary values that the client and idp agreed upon to communicate the level of authentication that happened. This is to give the client a level of confidence on the qualify of the authentication that took place.
                # "jti" : str(uuid.uuid4()),
                # # https://www.rfc-editor.org/rfc/rfc7519#section-4.1.7
                # 'aud': audience,
                ## https://www.rfc-editor.org/rfc/rfc7519#section-4.1.3
                "azp": client_from_db.client_id,
                "client_id": client_from_db.client_id,
                "client_uri": client_from_db.client_uri,
                # https://www.rfc-editor.org/rfc/rfc7519#section-4.1.2
                "sub": str(client_from_db.id),
                "scope": scopes,
                "typ": "Bearer",
                "exp": time.time() + expiration_time,
                "iat": time.time(),
                "iss": str(self.request.url).replace(
                    self.request.url.path, "/"
                ),  # https://www.rfc-editor.org/rfc/rfc7519#section-4.1.1
            }
        )
        response = {
            "access_token": access_token,
            "expires_in": expiration_time,
            "token_type": "Bearer",
            "refresh_expires_in": 0,
            "not_before_policy": 0,
            "scope": scopes,
        }
        return response

    async def revoke_token(self) -> None:

        token_type_hint = self.request_body.token_type_hint
        if token_type_hint == "refresh_token":
            logger.info("I am here")
            logger.info(f"{token_type_hint}")
            logger.info(f"{self.request_body.token}")
            if await self.persistent_grant_repo.exists(
                grant_type=token_type_hint, grant_data=self.request_body.token
            ):
                await self.persistent_grant_repo.delete(
                    grant_type=token_type_hint, 
                    grant_data=self.request_body.token
                )
            else:
                raise GrantNotFoundError
        elif token_type_hint == "access_token":
            # TODO: realize logic for access_token revocation.
            pass
        else:
            raise GrantNotFoundError
