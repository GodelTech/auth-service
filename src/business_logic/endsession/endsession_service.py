from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.business_logic.dependencies.database import get_repository_no_depends
from src.business_logic.services.jwt_token import JWTService

from .dto.request import RequestEndSessionModel
from .validators import (
                        ValidateDecodedIdTokenHint,
                        ValidateLogoutRedirectUri,
                        ValidateIdTokenHint
                        )

from typing import Union, Optional, Any
# from src.business_logic.common.interfaces import ValidatorProtocol


class EndSessionService:
    """
    Service for endsession endpoint ......
    """
    def __init__(
        self,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt_service: JWTService,
    ) -> None:
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.jwt_service = jwt_service
        # self._request_model: Optional[RequestEndSessionModel]= None
        # id_token_hint_validator: ValidatorProtocol = ValidateIdTokenHint
        # decoded_id_token_hint_validator: ValidatorProtocol = ValidateDecodedIdTokenHint
        # logout_redirect_uri_validator: ValidatorProtocol = ValidateLogoutRedirectUri

    async def end_session(self, request_model: RequestEndSessionModel) -> Optional[str]:
        # await id_token_hint_validator(request_model)
        decoded_id_token_hint = await self._decode_id_token_hint(id_token_hint=request_model.id_token_hint)
        # await decoded_id_token_hint_validator(decoded_id_token_hint: dict[str, Any])

        await self._logout(
            client_id=decoded_id_token_hint['client_id'],
            user_id=decoded_id_token_hint['sub']
        )

        if request_model.post_logout_redirect_uri:
            # ? await logout_redirect_uri_validator(request_model, decoded_id_token_hint["client_id"]: str)
            if await self._validate_logout_redirect_uri(
                logout_redirect_uri=request_model.post_logout_redirect_uri,
                client_id=decoded_id_token_hint["client_id"]
            ):
                logout_redirect_uri = request_model.post_logout_redirect_uri
                if request_model.state:
                    logout_redirect_uri += f"&state={request_model.state}"
                return logout_redirect_uri
        return None

    async def _decode_id_token_hint(self, id_token_hint: str) -> dict[str, Any]:
        decoded_data = await self.jwt_service.decode_token(token=id_token_hint)
        return decoded_data

    async def _logout(self, client_id: str, user_id: int) -> None:
        await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id=client_id,
            user_id=user_id
        )

    async def _validate_logout_redirect_uri(self, client_id: str, logout_redirect_uri: str) -> bool:
        result = await self.client_repo.validate_post_logout_redirect_uri(client_id, logout_redirect_uri)
        return result
