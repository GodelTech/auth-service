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


class ClientCredentialsTokenService:
    def __init__(
            self,
            grant_validator: ValidatorProtocol,
            redirect_uri_validator: ValidatorProtocol,
            client_validator: ValidatorProtocol,
            code_validator: ValidatorProtocol,
            grant_exp_validator: ValidatorProtocol,
            jwt_manager: JWTManagerProtocol,
            persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self._grant_validator = grant_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._client_validator = client_validator
        self._code_validator = code_validator
        self._grant_expiration_validator = grant_exp_validator
        self._jwt_manager = jwt_manager
        self._persistent_grant_repo = persistent_grant_repo

    async def get_tokens(self, data: RequestTokenModel) -> ResponseTokenModel:
        ...
