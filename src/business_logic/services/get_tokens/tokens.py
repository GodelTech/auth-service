import datetime
import logging
import time
import uuid
from typing import Any, Dict, Optional, Union


from src.business_logic.services.jwt_token import JWTService

from src.data_access.postgresql.repositories import (
    BlacklistedTokenRepository,
    ClientRepository,
    DeviceRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.dyna_config import DOMAIN_NAME
from src.presentation.api.models import (
    BodyRequestRevokeModel,
    BodyRequestTokenModel,
)
from .dto import RequestTokenModel, ResponseTokenModel


class TokenService:
    def __init__(
            self,
            client_repo: ClientRepository,
            persistent_grant_repo: PersistentGrantRepository,
            user_repo: UserRepository,
            device_repo: DeviceRepository,
            jwt_service: JWTService,
            blacklisted_repo: BlacklistedTokenRepository,
    ) -> None:
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.user_repo = user_repo
        self.device_repo = device_repo
        self.jwt_service = jwt_service
        self.blacklisted_repo = blacklisted_repo
    
    def get_tokens(self, request_data: RequestTokenModel) -> ResponseTokenModel:
        pass
