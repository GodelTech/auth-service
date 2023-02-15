from typing import Optional, Union

from fastapi import Depends

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.presentation.api.models.endsession import RequestEndSessionModel


class EndSessionService:
    def __init__(
        self,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt_service: JWTService,
    ) -> None:
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.jwt_service = jwt_service
        self._request_model: Optional[RequestEndSessionModel] = None

    async def end_session(self) -> Union[str, None]:
        if self.request_model is not None:
            decoded_id_token_hint = await self._decode_id_token_hint(
                id_token_hint=self.request_model.id_token_hint
            )
            sub = decoded_id_token_hint["sub"]
            await self._logout(
                client_id=decoded_id_token_hint["client_id"], user_id=int(sub)
            )
            if self.request_model.post_logout_redirect_uri:
                if await self._validate_logout_redirect_uri(
                    logout_redirect_uri=self.request_model.post_logout_redirect_uri,
                    client_id=decoded_id_token_hint["client_id"],
                ):
                    logout_redirect_uri = (
                        self.request_model.post_logout_redirect_uri
                    )
                    if self.request_model.state:
                        logout_redirect_uri += (
                            f"&state={self.request_model.state}"
                        )
                    return logout_redirect_uri
        return None

    async def _decode_id_token_hint(self, id_token_hint: str) -> dict[str, str]:
        decoded_data = await self.jwt_service.decode_token(token=id_token_hint)
        return decoded_data

    async def _logout(self, client_id: str, user_id: int) -> None:
        await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id=client_id, user_id=user_id
        )
        return

    async def _validate_logout_redirect_uri(
        self, client_id: str, logout_redirect_uri: str
    ) -> bool:
        result = await self.client_repo.validate_post_logout_redirect_uri(
            client_id, logout_redirect_uri
        )
        return result

    @property
    def request_model(self) -> Optional[RequestEndSessionModel]:
        return self._request_model

    @request_model.setter
    def request_model(self, model: Optional[RequestEndSessionModel]) -> None:
        if model is not None:
            self._request_model = model
