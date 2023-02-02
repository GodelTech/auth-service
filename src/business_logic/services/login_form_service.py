import logging

from src.data_access.postgresql.repositories import ClientRepository
from src.data_access.postgresql.errors import WrongResponseTypeError
from src.presentation.api.models import RequestModel

logger = logging.getLogger('is_app')


class LoginFormService:
    def __init__(
        self,
        client_repo: ClientRepository,
    ) -> None:
        self._request_model = None
        self.client_repo = client_repo

    async def get_html_form(self) -> bool:
        if await self._validate_client(self.request_model.client_id):

            if await self._validate_client_redirect_uri(
                client_id=self.request_model.client_id,
                redirect_uri=self.request_model.redirect_uri,
            ):
                if self.request_model.response_type in ["code", "token", "id_token token"]:
                    return True
                else:
                    raise WrongResponseTypeError("You try to pass unprocessable response type")

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.validate_client_by_client_id(
            client_id=client_id
        )
        return client

    async def _validate_client_redirect_uri(self, client_id: str, redirect_uri: str) -> bool:
        """
        Checks if the redirect uri is in the database.
        """
        client = await self.client_repo.validate_client_redirect_uri(
            client_id=client_id,
            redirect_uri=redirect_uri
        )
        return client

    @property
    def request_model(self) -> None:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestModel) -> None:
        self._request_model = request_model
