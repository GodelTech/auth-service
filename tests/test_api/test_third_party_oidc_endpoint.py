from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.tables.identity_resource import (
    IdentityProviderMapped,
    IdentityProviderState,
)

STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
SHORT_STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"


@pytest.mark.asyncio
class TestThirdPartyGitHubEndpoint:
    async def test_successful_github_request_get(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="e6a4c6014f35f4acf016",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "NewUserNew"

        patch_start = "src.business_logic.services.third_party_oidc_service.AuthThirdPartyOIDCService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )
        params = {"code": "test_code", "state": STUB_STATE}
        response = await client.request(
            "GET", "/authorize/oidc/github", params=params
        )
        assert response.status_code == status.HTTP_302_FOUND

        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 1,
                IdentityProviderMapped.provider_client_id
                == "e6a4c6014f35f4acf016",
                IdentityProviderMapped.provider_client_secret
                == "***REMOVED***",
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_github_request_get_index_error(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        expected_content = '{"message":"Error in parsing"}'

        await connection.execute(
            insert(IdentityProviderState).values(state=SHORT_STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="e6a4c6014f35f4acf016",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "NewUserNew"

        patch_start = "src.business_logic.services.third_party_oidc_service.AuthThirdPartyOIDCService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )
        params = {"code": "test_code", "state": SHORT_STUB_STATE}
        response = await client.request(
            "GET", "/authorize/oidc/github", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 1,
                IdentityProviderMapped.provider_client_id
                == "e6a4c6014f35f4acf016",
                IdentityProviderMapped.provider_client_secret
                == "***REMOVED***",
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == SHORT_STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_github_request_get_wrong_state(
        self, client: AsyncClient
    ) -> None:
        expected_content = '{"message":"Wrong data has been passed"}'

        params = {"code": "test_code", "state": "test_state"}
        response = await client.request(
            "GET", "/authorize/oidc/github", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content


@pytest.mark.asyncio
class TestCreateStateEndpoint:
    async def test_successful_create_state(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        content_type = "application/x-www-form-urlencoded"

        params = {
            "state": "some_new_state",
        }
        response = await client.request(
            "POST",
            "/authorize/oidc/state",
            data=params,
            headers={"Content-Type": content_type},
        )
        assert response.status_code == status.HTTP_200_OK
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == "some_new_state"
            )
        )
        await connection.commit()

    async def test_unsuccessful_create_state_duplication(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        expected_content = '{"message":"Third Party State already exists"}'

        await connection.execute(
            insert(IdentityProviderState).values(state="already_exists")
        )
        await connection.commit()

        content_type = "application/x-www-form-urlencoded"

        params = {
            "state": "already_exists",
        }
        response = await client.request(
            "POST",
            "/authorize/oidc/state",
            data=params,
            headers={"Content-Type": content_type},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.content.decode("UTF-8") == expected_content
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == "already_exists"
            )
        )
        await connection.commit()


@pytest.mark.asyncio
class TestThirdPartyGoogleEndpoint:
    async def test_successful_google_request_get(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=4,
                provider_client_id="419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGoogleService"

        mocker.patch(f"{patch_start}.get_google_access_token", replace_post)
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_email", replace_get
        )

        params = {
            "code": "test_code",
            "state": STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/google", params=params
        )
        assert response.status_code == status.HTTP_302_FOUND

        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 4,
                IdentityProviderMapped.provider_client_id
                == "419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                IdentityProviderMapped.provider_client_secret
                == "***REMOVED***",
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_google_request_get_index_error(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        expected_content = '{"message":"Error in parsing"}'

        await connection.execute(
            insert(IdentityProviderState).values(state=SHORT_STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=4,
                provider_client_id="419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGoogleService"

        mocker.patch(f"{patch_start}.get_google_access_token", replace_post)
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_email", replace_get
        )

        params = {
            "code": "test_code",
            "state": SHORT_STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/google", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 4,
                IdentityProviderMapped.provider_client_id
                == "419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                IdentityProviderMapped.provider_client_secret
                == "***REMOVED***",
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == SHORT_STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_google_request_get_wrong_state(
        self, client: AsyncClient
    ) -> None:
        expected_content = '{"message":"Wrong data has been passed"}'

        params = {
            "code": "test_code",
            "state": "test_state",
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/google", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content


@pytest.mark.asyncio
class TestThirdPartyGitlabEndpoint:
    async def test_successful_gitlab_request_get(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=5,
                provider_client_id="***REMOVED***",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "UserNewNickname"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGitLabService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        params = {
            "code": "test_code",
            "state": STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/gitlab", params=params
        )
        assert response.status_code == status.HTTP_302_FOUND

        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 5,
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_gitlab_request_get_index_error(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        expected_content = '{"message":"Error in parsing"}'

        await connection.execute(
            insert(IdentityProviderState).values(state=SHORT_STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=5,
                provider_client_id="***REMOVED***",
                provider_client_secret="***REMOVED***",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args, **kwargs) -> str:
            return "access_token"

        async def replace_get(*args, **kwargs) -> str:
            return "UserNewNickname"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGitLabService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        params = {
            "code": "test_code",
            "state": SHORT_STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/gitlab", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 5,
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == SHORT_STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_gitlab_request_get_wrong_state(
        self, client: AsyncClient
    ) -> None:
        expected_content = '{"message":"Wrong data has been passed"}'

        params = {
            "code": "test_code",
            "state": "test_state",
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/gitlab", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content


@pytest.mark.asyncio
class TestThirdPartyMicrosoftEndpoint:
    async def test_successful_gitlab_request_get(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=6,
                provider_client_id="***REMOVED***",
                provider_client_secret="5_e8Q~oGsgilQM-TofukM.HRPyiChks_lGsNwbpD",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> None:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> None:
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyMicrosoftService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        params = {
            "code": "test_code",
            "state": STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/microsoft", params=params
        )
        assert response.status_code == status.HTTP_302_FOUND

        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 6,
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_gitlab_request_get_index_error(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        expected_content = '{"message":"Error in parsing"}'

        await connection.execute(
            insert(IdentityProviderState).values(state=SHORT_STUB_STATE)
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=6,
                provider_client_id="***REMOVED***",
                provider_client_secret="5_e8Q~oGsgilQM-TofukM.HRPyiChks_lGsNwbpD",
                enabled=True,
            )
        )
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyMicrosoftService"

        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        params = {
            "code": "test_code",
            "state": SHORT_STUB_STATE,
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/microsoft", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 6,
            )
        )
        await connection.commit()
        await connection.execute(
            delete(IdentityProviderState).where(
                IdentityProviderState.state == SHORT_STUB_STATE
            )
        )
        await connection.commit()

    async def test_unsuccessful_microsoft_request_get_wrong_state(
        self, client: AsyncClient
    ) -> None:
        expected_content = '{"message":"Wrong data has been passed"}'

        params = {
            "code": "test_code",
            "state": "test_state",
            "scope": "test_scope",
        }
        response = await client.request(
            "GET", "/authorize/oidc/microsoft", params=params
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
