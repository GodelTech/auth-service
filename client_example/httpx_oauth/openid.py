from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import Request
from fastapi.responses import RedirectResponse

from .errors import GetIdError
from .oauth2 import BaseOAuth2, OAuth2Error

BASE_SCOPES = ["openid", "email"]


class OpenIDConfigurationError(OAuth2Error):
    pass


class OpenID(BaseOAuth2[Dict[str, Any]]):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        openid_configuration_endpoint: str,
        name: str = "openid",
        base_scopes: Optional[List[str]] = BASE_SCOPES,
    ):
        with httpx.Client() as client:
            response = client.get(openid_configuration_endpoint)
            if response.status_code >= 400:
                raise OpenIDConfigurationError(response.json())
            self.openid_configuration: Dict[str, Any] = response.json()

        token_endpoint = self.openid_configuration["token_endpoint"]
        refresh_token_supported = (
            "refresh_token"
            in self.openid_configuration.get("grant_types_supported", [])
        )

        super().__init__(
            client_id,
            client_secret,
            self.openid_configuration["authorization_endpoint"],
            self.openid_configuration["token_endpoint"],
            token_endpoint if refresh_token_supported else None,
            self.openid_configuration.get("revocation_endpoint"),
            name,
            base_scopes,
        )

    async def get_id(self, token: str) -> int:
        async with self.get_httpx_client() as client:
            response = await client.get(
                self.openid_configuration["userinfo_endpoint"],
                headers={
                    **self.request_headers,
                    "Authorization": f"Bearer {token}",
                },
            )

            if response.status_code >= 400:
                raise GetIdError(response.json())

            data: Dict[str, Any] = response.json()

            return int(data["sub"])

    async def logout(
        self,
        id_token_hint: str,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
    ) -> RedirectResponse:
        async with self.get_httpx_client() as client:
            params = {
                "id_token_hint": id_token_hint,
            }

            if redirect_uri is not None:
                params["post_logout_redirect_uri"] = redirect_uri

            if state is not None:
                params["state"] = state

            response = await client.get(
                url="http://localhost:8000/endsession/",
                params=params,
            )
            return response
