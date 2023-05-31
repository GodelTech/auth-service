from __future__ import annotations
import time
import uuid
from src.business_logic.get_tokens.dto import RequestTokenModel, ResponseTokenModel
from src.business_logic.jwt_manager.dto import AccessTokenPayload
from src.dyna_config import DOMAIN_NAME

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol
    from src.data_access.postgresql.repositories import PersistentGrantRepository


class ClientCredentialsTokenService:
    def __init__(
            self,
            client_credentials_validator: ValidatorProtocol,
            jwt_manager: JWTManagerProtocol,
            persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self._client_credentials_validator = client_credentials_validator
        self._jwt_manager = jwt_manager
        self._persistent_grant_repo = persistent_grant_repo

    async def get_tokens(self, data: RequestTokenModel) -> ResponseTokenModel:
        await self._client_credentials_validator(
            client_id=data.client_id, 
            client_secret=data.client_secret
        )

        current_unix_time = int(time.time())
        access_token = await self._get_access_token(request_data=data, unix_time=current_unix_time)

        return ResponseTokenModel(
            access_token=access_token,
            token_type="Bearer",
            expires_in=600,
            not_before_policy=0,
            scope=data.scope
        )

    async def _get_access_token(self, request_data: RequestTokenModel, unix_time: int) -> str:
        payload = AccessTokenPayload(
            sub=request_data.client_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            aud=["admin", "introspection", "revoke"],
            jti=str(uuid.uuid4()),
            acr=0
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')
