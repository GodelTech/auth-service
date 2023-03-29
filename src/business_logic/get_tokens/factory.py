from src.business_logic.get_tokens.service_impls import AuthorizationCodeTokenService
from src.business_logic.get_tokens.validators import ValidatePersistentGrant, ValidateRedirectUri
from src.business_logic.common.validators import ValidateClient
from src.business_logic.jwt_manager import JWTManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interfaces import TokenServiceProto
    from src.data_access.postgresql.repositories import (
        BlacklistedTokenRepository,
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )
    from src.business_logic.services import JWTService
    from src.business_logic.jwt_manager.interfaces import JWTServiceProto


class TokenServiceFactory:
    def __init__(
            self,
            client_repo: 'ClientRepository',
            persistent_grant_repo: 'PersistentGrantRepository',
            user_repo: 'UserRepository',
            device_repo: 'DeviceRepository',
            jwt_manager: 'JWTServiceProto',
            blacklisted_repo: 'BlacklistedTokenRepository',
    ) -> None:
        self._client_repo = client_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._device_repo = device_repo
        self._jwt_manager = jwt_manager
        self._blacklisted_repo = blacklisted_repo

    def get_service_impl(self, grant_type: str) -> 'TokenServiceProto':
        if grant_type == 'authorization_code':
            return AuthorizationCodeTokenService(
                grant_validator=ValidatePersistentGrant(persistent_grant_repo=self._persistent_grant_repo),
                redirect_uri_validator=ValidateRedirectUri(client_repo=self._client_repo),
                client_validator=ValidateClient(client_repo=self._client_repo),
                jwt_manager=self._jwt_manager
            )
