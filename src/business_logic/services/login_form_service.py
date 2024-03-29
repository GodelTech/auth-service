from __future__ import annotations
import logging
import secrets
from typing import Any, Dict, Optional, TYPE_CHECKING

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings.app import AppSettings
from src.data_access.postgresql.errors import WrongResponseTypeError
from src.data_access.postgresql.repositories import (
    ClientRepository,
    ThirdPartyOIDCRepository,
    CodeChallengeRepository,
)
from src.presentation.api.models import RequestModel
from src.data_access.postgresql.errors.client import ClientNotFoundError

logger = logging.getLogger(__name__)


class LoginFormService:
    def __init__(
        self,
        session: AsyncSession,
        client_repo: ClientRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        code_challenge_repo: CodeChallengeRepository,
    ) -> None:
        self._request_model: Optional[RequestModel] = None
        self.session = session
        self.client_repo = client_repo
        self.oidc_repo = oidc_repo
        self.code_challenge_repo = code_challenge_repo

    async def get_html_form(self) -> Optional[bool]:
        if self.request_model is not None:
            if await self._validate_client(self.request_model.client_id):
                if await self._validate_client_redirect_uri(
                    client_id=self.request_model.client_id,
                    redirect_uri=self.request_model.redirect_uri,
                ):
                    if self.request_model.response_type in [
                        "code",
                        "token",
                        "id_token",
                        "id_token token",
                        "urn:ietf:params:oauth:grant-type:device_code",
                    ]:
                        if self.request_model.response_type == "code" and (
                            self.request_model.code_challenge
                            and self.request_model.code_challenge_method
                        ):
                            await self._save_code_challenge()
                        return True
                    else:
                        raise WrongResponseTypeError(
                            "You try to pass unprocessable response type"
                        )
        return None

    async def form_providers_data_for_auth(
        self,
    ) -> Optional[Dict[str, Any]]:
        if self.request_model is not None:
            if await self._validate_client(self.request_model.client_id):
                providers_data: Dict[str, Any] = {}
                row_providers_data = (
                    await self.oidc_repo.get_row_providers_data()
                )
                for provider in row_providers_data:
                    state_fist_part = secrets.token_urlsafe(32)
                    state = "!_!".join(
                        [
                            state_fist_part,
                            self.request_model.client_id,
                            self.request_model.redirect_uri,
                        ]
                    )
                    # await self.oidc_repo.create_state(state=state)
                    provider_link = (
                        f"{provider[1]}?client_id={provider[2]}&"
                        f"redirect_uri={provider[3]}&state={state}&"
                        f"response_type={self.request_model.response_type}"
                    )
                    # TODO
                    if provider[0] == "gitlab":
                        provider_link += "&scope=openid"
                    else:
                        provider_link += "&scope=openid+profile+email"
                    providers_data[provider[0]] = {
                        "provider_icon": provider[5],
                        "provider_link": provider_link,
                    }
                return providers_data
            else:
                raise ClientNotFoundError
        return None

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.validate_client_by_client_id(
            client_id=client_id
        )
        return client

    async def _validate_client_redirect_uri(
        self, client_id: str, redirect_uri: str
    ) -> bool:
        """
        Checks if the redirect uri is in the database.
        """
        client = await self.client_repo.validate_client_redirect_uri(
            client_id=client_id, redirect_uri=redirect_uri
        )
        return client

    async def _save_code_challenge(self) -> None:
        code_challenge = self.request_model.code_challenge

        if self.request_model.code_challenge_method == "S256":
            fernet = Fernet(AppSettings().secret_key.get_secret_value())
            code_challenge = fernet.encrypt(code_challenge.encode()).decode()

        await self.code_challenge_repo.create(
            client_id=self.request_model.client_id,
            code_challenge_method=self.request_model.code_challenge_method,
            code_challenge=code_challenge,
        )

    @property
    def request_model(self) -> Optional[RequestModel]:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestModel) -> None:
        self._request_model = request_model
