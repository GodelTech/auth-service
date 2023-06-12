from __future__ import annotations
from src.business_logic.get_tokens.service_impls import (
    AuthorizationCodeTokenService,
    RefreshTokenGrantService,
    ClientCredentialsTokenService,
)
from src.business_logic.get_tokens.validators import (
    ValidatePersistentGrant, 
    ValidateRedirectUri, 
    ValidateGrantByClient,
    ValidateGrantExpired,
    ValidateClientCredentials,
)
from src.business_logic.get_tokens.errors import UnsupportedGrantTypeError
from src.business_logic.common.validators import ClientIdValidator, ScopeValidator

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from .interfaces import TokenServiceProtocol
    from src.data_access.postgresql.repositories import (
        BlacklistedTokenRepository,
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


class TokenServiceFactory:
    def __init__(
            self,
            session: AsyncSession,
            client_repo: ClientRepository,
            persistent_grant_repo: PersistentGrantRepository,
            user_repo: UserRepository,
            device_repo: DeviceRepository,
            jwt_manager: JWTManagerProtocol,
            blacklisted_repo: BlacklistedTokenRepository,
    ) -> None:
        self._session = session
        self._client_repo = client_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._device_repo = device_repo
        self._jwt_manager = jwt_manager
        self._blacklisted_repo = blacklisted_repo

    def get_service_impl(self, grant_type: str) -> TokenServiceProtocol:
        if grant_type == 'authorization_code':
            return AuthorizationCodeTokenService(
                session=self._session,
                grant_validator=ValidatePersistentGrant(persistent_grant_repo=self._persistent_grant_repo),
                redirect_uri_validator=ValidateRedirectUri(client_repo=self._client_repo),
                client_validator=ClientIdValidator(client_repo=self._client_repo),
                code_validator=ValidateGrantByClient(persistent_grant_repo=self._persistent_grant_repo),
                grant_exp_validator=ValidateGrantExpired(),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo
            )
        elif grant_type == 'refresh_token':
            return RefreshTokenGrantService(
                session=self._session,
                grant_validator=ValidatePersistentGrant(persistent_grant_repo=self._persistent_grant_repo),
                client_validator=ClientIdValidator(client_repo=self._client_repo),
                refresh_token_validator=ValidateGrantByClient(persistent_grant_repo=self._persistent_grant_repo),
                grant_exp_validator=ValidateGrantExpired(),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo
            )
        elif grant_type == 'client_credentials':
            return ClientCredentialsTokenService(
                client_credentials_validator=ValidateClientCredentials(client_repo=self._client_repo),
                scope_validator=ScopeValidator(client_repo=self._client_repo),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo
            )
        else:
            raise UnsupportedGrantTypeError
