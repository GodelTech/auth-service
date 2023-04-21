from __future__ import annotations
import time
import uuid
from src.business_logic.get_tokens.dto import RequestTokenModel, ResponseTokenModel
from src.business_logic.jwt_manager.dto import AccessTokenPayload, RefreshTokenPayload, IdTokenPayload
from src.dyna_config import DOMAIN_NAME
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol
    from src.data_access.postgresql.repositories import PersistentGrantRepository


class RefreshTokenGrantService:
    def __init__(
            self,
            grant_validator: ValidatorProtocol,
            client_validator: ValidatorProtocol,
            refresh_token_validator: ValidatorProtocol,
            grant_exp_validator: ValidatorProtocol,
            jwt_manager: JWTManagerProtocol,
            persistent_grant_repo: PersistentGrantRepository
    ):
        self._grant_validator = grant_validator
        self._client_validator = client_validator
        self._refresh_token_validator = refresh_token_validator
        self._grant_expiration_validator = grant_exp_validator
        self._jwt_manager = jwt_manager
        self._persistent_grant_repo = persistent_grant_repo

    async def get_tokens(self, request_data: RequestTokenModel) -> ResponseTokenModel:
        await self._client_validator(request_data.client_id)
        await self._refresh_token_validator(request_data.refresh_token, request_data.client_id, request_data.grant_type)
        await self._grant_validator(request_data.refresh_token, request_data.grant_type)

        grant = await self._persistent_grant_repo.get_grant(
            grant_type=request_data.grant_type, 
            grant_data=request_data.refresh_token
        )

        await self._grant_expiration_validator(grant.expiration)

        user_id = grant.user_id
        current_unix_time = int(time.time())

        access_token = await self._get_access_token(request_data=request_data, user_id=user_id, unix_time=current_unix_time)
        id_token = await self._get_id_token(request_data=request_data, user_id=user_id, unix_time=current_unix_time)
        
        return ResponseTokenModel(
            access_token=access_token,
            refresh_token=grant.grant_data,
            id_token=id_token,
            token_type='Bearer',
            expires_in=600,
            refresh_expires_in=1800
        )

    async def _get_access_token(self, request_data: RequestTokenModel, user_id: str, unix_time: int) -> str:
        payload = AccessTokenPayload(
            sub=user_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            aud=request_data.client_id,
            jti=str(uuid.uuid4()),
            acr=0,
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')

    async def _get_id_token(self, request_data: RequestTokenModel, user_id: str, unix_time: int) -> str:
        payload = IdTokenPayload(
            sub=user_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            aud=request_data.client_id,
            jti=str(uuid.uuid4()),
            acr=0,
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')
