from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any
import secrets
import json

if TYPE_CHECKING:
    from httpx import AsyncClient
    from src.business_logic.third_party_oidc.dto import (
        StateRequestModel,
        ThirdPartyProviderAccessTokenRequestModelBase,
    )

    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


class ThirdPartyOIDCService:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        http_client: AsyncClient,
    ) -> None:
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.oidc_repo = oidc_repo
        self.http_client = http_client

    @staticmethod
    def _parse_response_content(
        response_content: str,
    ) -> Dict[str, Any]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in response_content.split("&")
            if len(item.split("=")) == 2
        }

    async def _create_provider_state(
        self, state_request_model: StateRequestModel
    ) -> None:
        await self.oidc_repo.create_state(state=state_request_model.state)

    async def get_redirect_uri(
        self,
        request_data: ThirdPartyProviderAccessTokenRequestModelBase,
        provider_name: str,
    ) -> Optional[str]:
        provider_links = await self.get_provider_external_links(
            name=provider_name
        )
        access_token_url: str = ""
        user_data_url: str = ""
        if provider_links is not None:
            access_token_url = provider_links["token_endpoint_link"]
            user_data_url = provider_links["userinfo_link"]
        if await self.oidc_repo.validate_state(state=request_data.state):
            await self.oidc_repo.delete_state(state=request_data.state)
            request_params = await self.get_provider_auth_request_data(
                name=provider_name, code=request_data.code
            )

            # make request to access_token_url to get a request token
            access_token: str = ""
            if request_params is not None:
                access_token = await self.get_access_token(
                    method="POST",
                    access_url=access_token_url,
                    params=request_params,
                )

            # make request to user_data_url to get user information
            headers = {
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            user_name = await self.get_user_data(
                access_url=user_data_url, headers=headers
            )

            redirect_uri = request_data.state.split("!_!")[
                -1
            ]  # this redirect uri we return

            if not await self.user_repo.validate_user_by_username(
                username=user_name
            ):
                # create new user
                provider_id = await self.oidc_repo.get_provider_id_by_name(
                    name=provider_name
                )
                if provider_id is not None:
                    await self.create_new_user(
                        username=user_name, provider=provider_id
                    )

            # create new persistent grant
            secret_code = secrets.token_urlsafe(32)

            await self.create_new_persistent_grant(
                username=user_name,
                secret_code=secret_code,
                state=request_data.state,
            )
            ready_redirect_uri = await self._update_redirect_url_with_params(
                redirect_uri=redirect_uri, secret_code=secret_code
            )
            return ready_redirect_uri

    async def get_access_token(
        self, method: str, access_url: str, params: Dict[str, Any]
    ) -> str:
        response_data = await self.http_client.request(
            f"{method}",
            access_url,
            params=params,
            headers={"Accept": "application/json"},
        )
        response_content = json.loads(response_data.content)
        return response_content["access_token"]

    async def get_user_data(
        self, access_url: str, headers: Dict[str, Any]
    ) -> str:
        user_response = await self.http_client.request(
            "GET", access_url, headers=headers
        )
        user_response_content = json.loads(user_response.content)
        return user_response_content["login"]

    async def get_provider_auth_request_data(
        self, name: str, code: str
    ) -> Optional[Dict[str, Any]]:
        provider_row_data = (
            await self.oidc_repo.get_row_provider_credentials_by_name(
                name=name
            )
        )
        if provider_row_data is not None:
            request_params = {
                "client_id": provider_row_data[0],
                "client_secret": provider_row_data[1],
                "redirect_uri": provider_row_data[2],
                "code": code,
            }
            return request_params

    async def get_provider_external_links(
        self, name: str
    ) -> Optional[Dict[str, str]]:
        external_links = await self.oidc_repo.get_provider_external_links(
            name=name
        )
        if external_links is not None:
            provider_external_links = {
                "token_endpoint_link": external_links[0],
                "userinfo_link": external_links[1],
            }
            return provider_external_links
        return None

    async def create_new_user(self, username: str, provider: int) -> None:
        await self.user_repo.create(
            username=username, identity_provider_id=provider
        )

    async def create_new_persistent_grant(
        self, username: str, secret_code: str, state: str
    ) -> None:
        user = await self.user_repo.get_user_by_username(username=username)
        grant_data = {
            "client_id": state.split("!_!")[1],
            "grant_data": secret_code,
            "user_id": user.id,
            "grant_type": "authorization_code",
        }
        await self.persistent_grant_repo.create(**grant_data)

    async def _update_redirect_url_with_params(
        self, redirect_uri: str, secret_code: str
    ) -> Optional[str]:
        if self.request_model is not None:
            redirect_uri = f"{redirect_uri}?code={secret_code}"
            if self.request_model.state:
                redirect_uri += f"&state={self.request_model.state}"

            return redirect_uri
        return None
