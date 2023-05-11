from typing import Generator
from unittest.mock import MagicMock, _Mock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from src.business_logic.third_party_auth import ThirdPartyAuthServiceProtocol
from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthInvalidStateError,
    ThirdPartyAuthProviderInvalidRequestDataError,
    UnsupportedThirdPartyAuthProviderError,
)

GetServiceImpl = Generator[MagicMock, None, None]
GetServiceImplWithSideEffect = Generator[_Mock, None, None]


@pytest.fixture
def mocked_get_service_impl() -> GetServiceImpl:
    with patch(
        "src.presentation.api.routes.third_party_oidc_authorization.ThirdPartyAuthServiceFactory.get_service_impl"
    ) as mocked_data:
        mock_auth_service = MagicMock(spec=ThirdPartyAuthServiceProtocol)
        mock_auth_service.get_redirect_url.return_value = (
            "http://www.test.com/"
        )
        mocked_data.return_value = mock_auth_service
        yield mock_auth_service
        del mock_auth_service


@pytest.fixture
def mocked_get_service_impl_with_side_effect() -> GetServiceImplWithSideEffect:
    with patch(
        "src.presentation.api.routes.third_party_oidc_authorization.ThirdPartyAuthServiceFactory.get_service_impl"
    ) as mocked_data:
        mocked_data.side_effect = UnsupportedThirdPartyAuthProviderError
        yield mocked_data
        del mocked_data


@pytest.mark.asyncio
class TestCreateState:
    @patch(
        "src.presentation.api.routes.third_party_oidc_authorization.ThirdPartyAuthServiceFactory.create_provider_state"
    )
    async def test_successful_create_state_request(
        self, mocked_data: _Mock, client: AsyncClient
    ) -> None:
        mocked_data.return_value = "test"
        response = await client.post(
            "/authorize/oidc/state",
            data={"state": "some_state"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "State created successfully"}

    @patch(
        "src.presentation.api.routes.third_party_oidc_authorization.ThirdPartyAuthServiceFactory.create_provider_state"
    )
    async def test_unsuccessful_create_state_request(
        self, mocked_data: _Mock, client: AsyncClient
    ) -> None:
        mocked_data.side_effect = ThirdPartyAuthInvalidStateError
        response = await client.post(
            "/authorize/oidc/state",
            data={"state": "some_state"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}


@pytest.mark.asyncio
class TestGithubAuthEndpoint:
    async def test_successful_github_get_request(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/github",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "http://www.test.com/"

    async def test_unsuccessful_github_get_request_invalid_state(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthInvalidStateError
        )
        response = await client.get(
            "/authorize/oidc/github",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}

    async def test_unsuccessful_github_get_request_invalid_request_data(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthProviderInvalidRequestDataError(
                "invalid_request_data"
            )
        )
        response = await client.get(
            "/authorize/oidc/github",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_request_data"}

    async def test_unsuccessful_github_get_request_unsupported_provider(
        self,
        mocked_get_service_impl_with_side_effect: _Mock,
        client: AsyncClient,
    ) -> None:
        response = await client.get(
            "/authorize/oidc/github",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "unsupported_auth_provider"}

    async def test_unsuccessful_github_get_request_without_state_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/github",
            params={"code": "test_code"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_github_get_request_without_code_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/github",
            params={"state": "test_state"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestLinkedinAuthEndpoint:
    async def test_successful_linkedin_get_request(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "http://www.test.com/"

    async def test_unsuccessful_linkedin_get_request_invalid_state(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthInvalidStateError
        )
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}

    async def test_unsuccessful_linkedin_get_request_invalid_request_data(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthProviderInvalidRequestDataError(
                "invalid_request_data"
            )
        )
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_request_data"}

    async def test_unsuccessful_linkedin_get_request_unsupported_provider(
        self,
        mocked_get_service_impl_with_side_effect: _Mock,
        client: AsyncClient,
    ) -> None:
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "unsupported_auth_provider"}

    async def test_unsuccessful_linkedin_get_request_without_state_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"code": "test_code"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_linkedin_get_request_without_code_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/linkedin",
            params={"state": "test_state"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestGoogleAuthEndpoint:
    async def test_successful_google_get_request(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/google",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "http://www.test.com/"

    async def test_unsuccessful_google_get_request_invalid_state(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthInvalidStateError
        )
        response = await client.get(
            "/authorize/oidc/google",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}

    async def test_unsuccessful_google_get_request_invalid_request_data(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthProviderInvalidRequestDataError(
                "invalid_request_data"
            )
        )
        response = await client.get(
            "/authorize/oidc/google",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_request_data"}

    async def test_unsuccessful_google_get_request_unsupported_provider(
        self,
        mocked_get_service_impl_with_side_effect: _Mock,
        client: AsyncClient,
    ) -> None:
        response = await client.get(
            "/authorize/oidc/google",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "unsupported_auth_provider"}

    async def test_unsuccessful_google_get_request_without_state_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/google",
            params={"code": "test_code"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_google_get_request_without_code_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/google",
            params={"state": "test_state"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestGitlabAuthEndpoint:
    async def test_successful_gitlab_get_request(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "http://www.test.com/"

    async def test_unsuccessful_gitlab_get_request_invalid_state(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthInvalidStateError
        )
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}

    async def test_unsuccessful_gitlab_get_request_invalid_request_data(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthProviderInvalidRequestDataError(
                "invalid_request_data"
            )
        )
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_request_data"}

    async def test_unsuccessful_gitlab_get_request_unsupported_provider(
        self,
        mocked_get_service_impl_with_side_effect: _Mock,
        client: AsyncClient,
    ) -> None:
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "unsupported_auth_provider"}

    async def test_unsuccessful_gitlab_get_request_without_state_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"code": "test_code"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_gitlab_get_request_without_code_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/gitlab",
            params={"state": "test_state"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestMicrosoftAuthEndpoint:
    async def test_successful_microsoft_get_request(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "http://www.test.com/"

    async def test_unsuccessful_microsoft_get_request_invalid_state(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthInvalidStateError
        )
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_state"}

    async def test_unsuccessful_microsoft_get_request_invalid_request_data(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        mocked_get_service_impl.get_redirect_url.side_effect = (
            ThirdPartyAuthProviderInvalidRequestDataError(
                "invalid_request_data"
            )
        )
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "invalid_request_data"}

    async def test_unsuccessful_microsoft_get_request_unsupported_provider(
        self,
        mocked_get_service_impl_with_side_effect: _Mock,
        client: AsyncClient,
    ) -> None:
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"code": "test_code", "state": "state"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "unsupported_auth_provider"}

    async def test_unsuccessful_microsoft_get_request_without_state_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"code": "test_code"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_unsuccessful_microsoft_get_request_without_code_parameter(
        self, mocked_get_service_impl: _Mock, client: AsyncClient
    ) -> None:
        response = await client.get(
            "/authorize/oidc/microsoft",
            params={"state": "test_state"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
