from __future__ import annotations
import time
import uuid
from src.business_logic.get_tokens.dto import RequestTokenModel, ResponseTokenModel
from src.business_logic.jwt_manager.dto import AccessTokenPayload
from src.dyna_config import DOMAIN_NAME

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol
    from src.data_access.postgresql.repositories import PersistentGrantRepository
from src.business_logic.services.scope import ScopeService

class ClientCredentialsTokenService:
    def __init__(
            self,
            session: AsyncSession,
            client_credentials_validator: ValidatorProtocol,
            scope_validator: ValidatorProtocol,
            jwt_manager: JWTManagerProtocol,
            persistent_grant_repo: PersistentGrantRepository,
            scope_service: ScopeService,
    ) -> None:
        self._session = session
        self._client_credentials_validator = client_credentials_validator
        self._scope_validator = scope_validator
        self._jwt_manager = jwt_manager
        self._persistent_grant_repo = persistent_grant_repo
        self._scope_service = scope_service

    async def get_tokens(self, data: RequestTokenModel) -> ResponseTokenModel:
        await self._client_credentials_validator(client_id=data.client_id, client_secret=data.client_secret)
        if data.scope:
            scopes = data.scope.split()
            await self._scope_validator(client_id=data.client_id, scopes=scopes)
        else:
            data.scope = ''
        current_unix_time = int(time.time())
        aud = data.scope.split(' ') + await self._scope_service.get_revoke_introspection_aud(name='oidc')
        access_token = await self._get_access_token(request_data=data, unix_time=current_unix_time, aud=aud)

        return ResponseTokenModel(
            access_token=access_token,
            token_type="Bearer",
            expires_in=600,
            not_before_policy=0,
            scope=data.scope
        )

    async def _get_access_token(self, request_data: RequestTokenModel, unix_time: int, aud: list[str]) -> str:
        payload = AccessTokenPayload(
            sub=request_data.client_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            aud=aud,
            jti=str(uuid.uuid4()),
            acr=0
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')
