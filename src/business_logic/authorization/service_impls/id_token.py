from __future__ import annotations

import time
import uuid

from typing import TYPE_CHECKING

from src.business_logic.authorization.mixins import UpdateRedirectUrlMixin
from src.business_logic.jwt_manager.dto import IdTokenPayload
from src.dyna_config import DOMAIN_NAME


if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.data_access.postgresql.repositories import (
        UserRepository,
    )
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


class IdTokenAuthService(UpdateRedirectUrlMixin):
    """
    Service for handling ID token generation and redirect URL construction in an authentication system.

    Inherits:
        UpdateRedirectUrlMixin, which provides functionality for updating
        the redirect URL with additional state parameter if it's present in a request model.


    Reference: https://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth
    """

    def __init__(
        self,
        client_validator: ValidatorProtocol,
        redirect_uri_validator: ValidatorProtocol,
        scope_validator: ValidatorProtocol,
        user_credentials_validator: ValidatorProtocol,
        user_repo: UserRepository,
        jwt_manager: JWTManagerProtocol,
    ) -> None:
        """
        Args:
            client_validator: A validator for client identification.
            redirect_uri_validator: A validator for redirect URIs.
            scope_validator: A validator for scope values.
            user_credentials_validator: A validator for user credentials.
            user_repo: A repository for managing users.
            jwt_manager: A manager for JWT encoding and decoding.

        """
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._scope_validator = scope_validator
        self._user_credentials_validator = user_credentials_validator
        self._user_repo = user_repo
        self._jwt_manager = jwt_manager
        self.expiration_time = 600

    async def _validate_request_data(self, request_data: AuthRequestModel):
        """
        Validate the request data for ID token generation.

        Args:
            request_data: An instance of AuthRequestModel containing the request data.

        Raises:
            Various validation errors based on the request data.
        """
        await self._client_validator(request_data.client_id)
        await self._redirect_uri_validator(
            request_data.redirect_uri, request_data.client_id
        )
        await self._scope_validator(request_data.scope, request_data.client_id)
        await self._user_credentials_validator(
            request_data.username, request_data.password
        )

    async def _get_id_token(
        self, request_data: AuthRequestModel, user_id: int, unix_time: int
    ) -> str:
        """
        Generate an ID token based on the provided request data, user ID, and Unix time.

        Args:
            request_data: An instance of AuthRequestModel containing the request data.
            user_id: The ID of the user.
            unix_time: The current Unix time.

        Returns:
            The generated ID token as a string.
        """
        payload = IdTokenPayload(
            sub=user_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + self.expiration_time,
            jti=str(uuid.uuid4()),
            acr=0,
        )
        return self._jwt_manager.encode(payload=payload, algorithm="RS256")

    async def get_redirect_url(self, request_data: AuthRequestModel) -> str:
        """
        Get the redirect URL with the ID token.

        Args:
            request_data: An instance of AuthRequestModel containing the request data.

        Returns:
            The redirect URL containing the ID token.

        Raises:
            Various validation errors based on the request data.
        """
        await self._validate_request_data(request_data)

        current_unix_time = int(time.time())
        user_id = (
            await self._user_repo.get_user_by_username(request_data.username)
        ).id

        id_token = await self._get_id_token(
            request_data=request_data,
            user_id=user_id,
            unix_time=current_unix_time,
        )
        redirect_url = f"{request_data.redirect_uri}?id_token={id_token}"

        return await self._update_redirect_url(request_data, redirect_url)
