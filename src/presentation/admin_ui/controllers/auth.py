import logging

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from typing import Union
from fastapi.responses import RedirectResponse
from src.business_logic.dto import AdminCredentialsDTO
from src.business_logic.services import AdminAuthService

logger = logging.getLogger(__name__)


class AdminAuthController(AuthenticationBackend):
    def __init__(self, secret_key: str, auth_service: AdminAuthService) -> None:
        self.auth_service = auth_service
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        data_from_form = await request.form()
        try:
            token = await self.auth_service.authorize(
                credentials=AdminCredentialsDTO(
                    username=data_from_form.get("username"),
                    password=data_from_form.get("password"),
                )
            )
            request.session.update({"Token": token})
            return True
        # TODO: Add different error types support!
        except Exception as e:
            logger.error(e)
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[None, RedirectResponse]:
        token = request.session.get("Token")
        return await self.auth_service.authenticate(token)
