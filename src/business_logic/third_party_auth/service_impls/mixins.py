import json
import time

from src.business_logic.third_party_auth.constants import StateData
from src.business_logic.third_party_auth.dto import (
    ThirdPartyAccessTokenRequestModel,
)
from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthProviderInvalidRequestDataError,
)
from src.business_logic.third_party_auth.interfaces import (
    ThirdPartyAuthMixinProtocol,
)


class ThirdPartyAuthMixin:
    """
    Mixin class providing common methods for third-party authentication.

    This class includes methods for forming parameter data, retrieving access tokens,
    obtaining usernames, creating users if they do not exist, creating grants,
    and updating redirect URLs.
    """

    async def _form_parameters_data(
        self: ThirdPartyAuthMixinProtocol,
        request_data: ThirdPartyAccessTokenRequestModel,
        provider_name: str,
    ) -> dict[str, str]:
        """
        Form the parameter data for making HTTP requests to obtain access tokens.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the necessary information.
            provider_name (str): The name of the third-party provider.

        Returns:
            dict[str, str]: The formed parameter data.
        """
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
        self: ThirdPartyAuthMixinProtocol,
        request_data: ThirdPartyAccessTokenRequestModel,
        token_url: str,
        provider_name: str,
    ) -> str:
        """
        Retrieve the access token from the third-party provider.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the necessary information.
            token_url (str): The URL for obtaining the access token.
            provider_name (str): The name of the third-party provider.

        Returns:
            str: The access token.

        Raises:
            ThirdPartyAuthProviderInvalidRequestDataError: If the request to the third-party provider returns an error response.
        """
        params = await self._form_parameters_data(request_data, provider_name)
        response = await self._async_http_client.request(
            "POST",
            token_url,
            params=params,
            headers={"Accept": "application/json"},
        )
        error_response = json.loads(response.content).get("error")
        if error_response:
            raise ThirdPartyAuthProviderInvalidRequestDataError(error_response)

        return json.loads(response.content)["access_token"]

    async def _get_username(
        self: ThirdPartyAuthMixinProtocol,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> str:
        """
        Retrieve the username from the third-party provider.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the necessary information.
            username_type (str): The type of username to retrieve based on third party provider docs (e.g., email).
            provider_name (str): The name of the third-party provider.

        Returns:
            str: The retrieved username.
        """
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
        self: ThirdPartyAuthMixinProtocol,
        username: str,
        provider_name: str,
    ) -> None:
        """
        Create a user if it does not already exist.

        Args:
            username (str): The username of the user.
            provider_name (str): The name of the third-party provider.
        """
        if not await self._user_repo.exists_user(username):
            provider_id = await self._oidc_repo.get_id_by_provider_name(
                provider_name
            )
            await self._user_repo.create(
                username=username, identity_provider_id=provider_id
            )

    async def _create_grant(
        self: ThirdPartyAuthMixinProtocol,
        request_data: ThirdPartyAccessTokenRequestModel,
        username_type: str,
        provider_name: str,
    ) -> None:
        """
        Create a persistent grant for the user. We need this grant to get an access
        token later on in an authorization process of our auth server.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the necessary information.
            username_type (str): The type of username to retrieve (e.g., email).
            provider_name (str): The name of the third-party provider.
        """
        username = await self._get_username(
            request_data=request_data,
            username_type=username_type,
            provider_name=provider_name,
        )
        await self._create_user_if_not_exists(username, provider_name)
        client_id = request_data.state.split("!_!")[StateData.CLIENT_ID.value]
        auth_code_lifetime = (
            await self._client_repo.get_auth_code_lifetime_by_client(client_id)
        )
        await self._persistent_grant_repo.create(
            client_id=client_id,
            grant_data=self._secret_code,
            user_id=await self._user_repo.get_user_id_by_username(username),
            grant_type="authorization_code",
            expiration_time=auth_code_lifetime + int(time.time()),
        )

    async def _update_redirect_url(
        self: ThirdPartyAuthMixinProtocol,
        request_data: ThirdPartyAccessTokenRequestModel,
        redirect_url: str,
    ) -> str:
        """
        Update the redirect URL with additional parameters.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the necessary information.
            redirect_url (str): The original redirect URL.

        Returns:
            str: The updated redirect URL.
        """
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url
