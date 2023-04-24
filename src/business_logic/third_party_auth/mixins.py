import json
import time
from src.business_logic.third_party_auth.dto import (
    ThirdPartyAccessTokenRequestModel,
)


class ThirdPartyAuthMixin:
    async def _form_parameters_data(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        provider_name: str,
    ):
        (
            provider_client_id,
            provider_client_secret,
            internal_redirect_uri,
        ) = await self._oidc_repo.get_credentials_by_provider_name(
            provider_name
        )
        return {
            "client_id": provider_client_id,
            "client_secret": provider_client_secret,
            "redirect_uri": internal_redirect_uri,
            "code": request_data.code,
            "grant_type": request_data.grant_type,
        }

    async def _get_access_token(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        token_url: str,
        provider_name: str,
    ) -> str:
        params = await self._form_parameters_data(request_data, provider_name)
        response = await self._async_http_client.request(
            "POST",
            token_url,
            params=params,
            headers={"Accept": "application/json"},
        )
        return json.loads(response.content)["access_token"]

    async def _get_username(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> str:
        (
            token_url,
            user_info_url,
        ) = await self._oidc_repo.get_external_links_by_provider_name(
            provider_name
        )
        access_token = await self._get_access_token(
            request_data, token_url, provider_name
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await self._async_http_client.request(
            "GET", user_info_url, headers=headers
        )
        return json.loads(response.content)[username_type]

    async def _create_user_if_not_exists(
        self, username: str, provider_name: str
    ):
        if not await self._user_repo.exists_user(username):
            provider_id = await self._oidc_repo.get_id_by_provider_name(
                provider_name
            )
            await self._user_repo.create(
                username=username, identity_provider_id=provider_id
            )

    async def _create__grant(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> None:
        username = await self._get_username(
            request_data=request_data,
            username_type=username_type,
            provider_name=provider_name,
        )
        await self._create_user_if_not_exists(username, provider_name)
        client_id = request_data.state.split("!_!")[1]
        # auth_code_lifetime = (
        #     await self._client_repo.get_auth_code_lifetime_by_client(client_id)
        # )
        grant_data = {
            "client_id": client_id,
            "grant_data": self._secret_code,
            "user_id": await self._user_repo.get_user_id_by_username(username),
            "grant_type": "authorization_code",
            # "expiration_time": auth_code_lifetime + int(time.time()),
        }
        await self._persistent_grant_repo.create(**grant_data)

    async def _update_redirect_url(
        self,
        request_data: ThirdPartyAccessTokenRequestModel,
        redirect_url: str,
    ) -> str:
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url
