import datetime
import logging
import time
import uuid
from typing import Any, Optional, Union
from src.dyna_config import BASE_URL
from fastapi import Request

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    DeviceCodeExpirationTimeError,
    DeviceCodeNotFoundError,
    DeviceRegistrationError,
    GrantNotFoundError,
    WrongGrantsError,
)
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models import (
    BodyRequestRevokeModel,
    BodyRequestTokenModel,
)
from src.data_access.postgresql.errors import ClaimsNotFoundError
logger = logging.getLogger(__name__)
from jwt.exceptions import ExpiredSignatureError

def get_base_payload(
    client_id: str, expiration_time: int, scope = None, claims = None, **kwargs: Any, 
) -> dict[str, Any]:
    if kwargs.get("user_id") and kwargs["user_id"] != "":
        kwargs["sub"] = kwargs.get("user_id")

    if kwargs.get("user_id"):
        kwargs.pop("user_id")

    base_payload = {
        "iss": f"http://{BASE_URL}",
        "client_id": client_id,
        "iat": int(time.time()),
        "exp": int(time.time() + expiration_time),
    } | kwargs
    if claims:
        base_payload['claims'] = claims
    if scope:
        base_payload = base_payload | scope
    return base_payload

async def get_single_token(
    client_id: str,
    jwt_service: JWTService,
    expiration_time: int,
    scope: Optional[str] = None, 
    **kwargs: Any,
) -> str:
    """
    It can be used for id, access and refresh token.
    'Additional data' means scopes for access/refresh token and claims for id token
    """
    base_payload = get_base_payload(
        # user_id=user_id,
        client_id=client_id,
        expiration_time=expiration_time,
        scope=scope,
        **kwargs,
    )
    full_payload = {**base_payload}
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
        self.request: Optional[Request] = None
        self.request_model: Optional[BodyRequestTokenModel] = None
        self.request_body: Optional[BodyRequestRevokeModel] = None
        self.authorization: Optional[str] = None
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.jwt_service = jwt_service

    async def get_tokens(self) -> dict[str, Any]:
        if self.request_model is None or self.request_model.grant_type is None:
            pass
        elif self.request_model.grant_type == "code":
            if self.request_model.redirect_uri is None or self.request_model.code is None:
                pass
            else:
                service = CodeMaker(token_service=self)
                return await service.create()
                
        elif self.request_model.grant_type == "password": 
            if self.request_model.username is None or self.request_model.password is None:
                pass
            else:
                return None
 
        elif self.request_model.grant_type == "refresh_token":
            if self.request_model.refresh_token is None:
                pass
            else:
                service = RefreshMaker(token_service=self)
                return await service.create()

        elif self.request_model.grant_type== "urn:ietf:params:oauth:grant-type:device_code":
            if self.request_model.device_code is None:
                pass
            else:
                service = DeviceCodeMaker(token_service=self)
                return await service.create()

        elif self.request_model.grant_type == "client_credentials":
            if self.request_model.client_secret is None:
                pass
            else:
                service = ClientCredentialsMaker(token_service=self)
                return await service.create()
        
        raise GrantNotFoundError

    async def revoke_token(self) -> None:
        if self.request_body is None:
            raise ValueError
        token_type_hint = self.request_body.token_type_hint
        if token_type_hint == "refresh_token":
            logger.debug("I am here")
            logger.debug(f"{token_type_hint}")
            logger.debug(f"{self.request_body.token}")
            if await self.persistent_grant_repo.exists(
                grant_type=token_type_hint, grant_data=self.request_body.token
            ):
                await self.persistent_grant_repo.delete(
                    grant_type=token_type_hint,
                    grant_data=self.request_body.token,
                )
            else:
                raise GrantNotFoundError
        elif token_type_hint == "access_token":
            # TODO: realize logic for access_token revocation.
            pass
        else:
            raise GrantNotFoundError


class BaseMaker:
    def __init__(self, token_service: TokenService) -> None:
        self.expiration_time = 600
        self.request_model: BodyRequestTokenModel= token_service.request_model
        self.client_repo: ClientRepository = token_service.client_repo
        self.persistent_grant_repo: PersistentGrantRepository = token_service.persistent_grant_repo
        self.user_repo: UserRepository = token_service.user_repo
        self.jwt_service: JWTService = token_service.jwt_service

    async def validation(self) -> None:
        encoded_attr:Optional[str] = None

        if self.request_model.grant_type == "urn:ietf:params:oauth:grant-type:device_code":
            encoded_attr = self.request_model.device_code
        else:
            encoded_attr = getattr(self.request_model, self.request_model.grant_type)

        if not await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    grant_data=encoded_attr,
                ):
            raise GrantNotFoundError
            
    async def make_tokens(self, create_id_token: bool = True, create_refresh_token: bool = True) -> dict[str, str]:
        if self.request_model.grant_type == "urn:ietf:params:oauth:grant-type:device_code":
            encoded_attr = self.request_model.device_code
        else:
            encoded_attr = getattr(self.request_model, self.request_model.grant_type)
        grant = await self.persistent_grant_repo.get(
                        grant_type=self.request_model.grant_type,
                        grant_data=encoded_attr
                    )
        client_id = self.request_model.client_id
        if client_id is None and (await self.client_repo.get_client_secrete_by_client_id(client_id=client_id) != self.request_model.client_secret):
                raise ClientNotFoundError    
        if grant.client.client_id != client_id:
            raise WrongGrantsError(
                "Client from request has been found in the database\
                but don't have provided grants"
            )
        

        user_id = grant.user_id
        scopes = {"scope": self.request_model.scope}
        
        # ACCESS TOKEN
        new_access_token = await get_single_token(
            user_id=user_id,
            client_id=client_id,
            scope=scopes,
            jwt_service=self.jwt_service,
            expiration_time=self.expiration_time * 6,
        )
        # ID TOKEN  
        new_id_token = None   
        if create_id_token:
            claims = None
            try:
                claims = await self.user_repo.get_claims(user_id)
                new_id_token = await get_single_token(
                    user_id=user_id,
                    client_id=client_id,
                    claims=claims,
                    scope=None,
                    jwt_service=self.jwt_service,
                    expiration_time=self.expiration_time
                )
            except ClaimsNotFoundError:
                
                new_id_token = await get_single_token(
                user_id=user_id,
                client_id=client_id,
                #TODO: fix e2e tests or add claims for users
                scope=None,
                claims=None,
                jwt_service=self.jwt_service,
                expiration_time=self.expiration_time,
            )
        
        # REFRESH TOKEN
        new_refresh_token = None
        if create_refresh_token:
            new_refresh_token = await get_single_token(
                                user_id=user_id,
                                client_id=client_id,
                                scope=scopes,
                                jwt_service=self.jwt_service,
                                expiration_time=self.expiration_time * 6,
                            )

            await self.persistent_grant_repo.create(
                client_id=client_id,
                grant_data=new_refresh_token,
                expiration_time=self.expiration_time * 6,
                user_id=user_id,
                grant_type="refresh_token",
            )
            # delete_old_refresh
            await self.persistent_grant_repo.delete(
                grant_data=self.request_model.code,
                grant_type=self.request_model.grant_type,
            )
        return {
            "access_token" : new_access_token,
            "refresh_token" : new_refresh_token,
            "id_token": new_id_token,
        }
        
class CodeMaker(BaseMaker):
    async def create(self) -> dict[str, Any]:
        await self.validation()
        tokens = await self.make_tokens()
        return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "id_token": tokens["id_token"],
                "expires_in": self.expiration_time,
                "token_type": "Bearer",
                }
    
class DeviceCodeMaker(BaseMaker):
    def __init__(self, token_service: TokenService) -> None:
        super().__init__(token_service)
        self.device_repo: DeviceRepository = token_service.device_repo

    async def device_validation(self) -> None:
        if not await self.persistent_grant_repo.exists(
                    grant_type=self.request_model.grant_type,
                    grant_data=self.request_model.device_code,
                ):
            if await self.device_repo.validate_device_code(
                device_code=self.request_model.device_code
            ):
                # add check for expire time
                now = datetime.datetime.utcnow()
                check_time = datetime.datetime.timestamp(now)
                expire_in = await self.device_repo.get_expiration_time(
                    device_code=self.request_model.device_code
                )
                if check_time > expire_in:
                    await self.device_repo.delete_by_device_code(
                        device_code=self.request_model.device_code
                    )
                    raise DeviceCodeExpirationTimeError(
                        "Device code expired"
                    )
                raise DeviceRegistrationError(
                    "Device registration in progress"
                )
        elif (
            self.request_model.device_code is None
            or not await self.persistent_grant_repo.exists(
                grant_type=self.request_model.grant_type,
                grant_data=self.request_model.device_code,
            )
        ):
            raise GrantNotFoundError

    async def create(self) -> dict[str, Any]:
        
        await self.device_validation()
        await self.validation()
        tokens = await self.make_tokens(create_id_token = False)
        return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": self.expiration_time,
                "token_type": "Bearer",
                }
    
class RefreshMaker(BaseMaker):
    async def create(self) -> dict[str: Any]:
        await self.validation()
        incoming_refresh_token = self.request_model.refresh_token
        try:    
            await self.jwt_service.decode_token(incoming_refresh_token)
            tokens = await self.make_tokens(create_refresh_token=False)
            return {
                    "access_token": tokens["access_token"],
                    "refresh_token": incoming_refresh_token,
                    "id_token": tokens["id_token"],
                    "expires_in": self.expiration_time,
                    "token_type": "Bearer",
                    }
        except ExpiredSignatureError:
            tokens = await self.make_tokens()
            return {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "id_token": tokens["id_token"],
                    "expires_in": self.expiration_time,
                    "token_type": "Bearer",
                    }

class ClientCredentialsMaker(BaseMaker):
    async def create(self) -> dict[str: Any]:
        client_from_db = ...
        if self.request_model is None:
            raise ValueError
        try:
            client_from_db = await self.client_repo.get_client_by_client_id(
                client_id=self.request_model.client_id
            )
            if not self.request_model.client_id:
                raise ClientNotFoundError
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

        if len(scopes) == 0:
            scopes = ["No scope"]

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
                "exp": time.time() + self.expiration_time,
                "iat": time.time(),
                "iss": f"http://{BASE_URL}"

                 # https://www.rfc-editor.org/rfc/rfc7519#section-4.1.1
            }
        )
        return {
            "access_token": access_token,
            "expires_in": self.expiration_time,
            "token_type": "Bearer",
            "refresh_expires_in": 0,
            "not_before_policy": 0,
            "scope": scopes,
        }


    