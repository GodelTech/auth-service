from unittest.mock import MagicMock, patch

import httpx
import pytest
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.errors import ThirdPartyStateDuplicationError
from src.data_access.postgresql.errors.user import DuplicationError
from src.data_access.postgresql.tables import IdentityProviderMapped
from src.data_access.postgresql.tables.identity_resource import (
    IdentityProviderState,
)
from tests.test_unit.fixtures import (
    state_request_model,
    third_party_oidc_request_model,
    third_party_google_request_model,
)
from src.business_logic.services import (
    AuthThirdPartyOIDCService,
    ThirdPartyGoogleService,
)
from typing import Any
from src.presentation.api.models import (
    ThirdPartyOIDCRequestModel,
    StateRequestModel,
    ThirdPartyGoogleRequestModel,
)

STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"


@pytest.mark.asyncio
class TestAuthorizationService:
    async def test_get_provider_auth_request_data(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        connection: AsyncSession,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
    ) -> None:
        service = auth_third_party_service
        service.request_model = third_party_oidc_request_model
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="test_client",
                provider_client_secret="secret",
                enabled=True,
            )
        )
        await connection.commit()
        expected_data = {
            "client_id": "test_client",
            "client_secret": "secret",
            "redirect_uri": "http://127.0.0.1:8000/authorize/oidc/github",
            "code": "test_code",
        }
        result_data = await service.get_provider_auth_request_data(
            name="github"
        )
        assert expected_data == result_data
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.provider_client_id == "test_client"
            )
        )
        await connection.commit()

    async def test_get_provider_auth_request_data_no_request_model(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        service = auth_third_party_service
        result_url = await service.get_provider_auth_request_data(
            name="No_such_a_provider"
        )
        assert result_url is None

    async def test_get_provider_external_links(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        expected_links = {
            "token_endpoint_link": "https://github.com/login/oauth/access_token",
            "userinfo_link": "https://api.github.com/user",
        }

        result_links = (
            await auth_third_party_service.get_provider_external_links(
                name="github"
            )
        )
        assert result_links == expected_links

    async def test_get_provider_external_links_not_registered_provider(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        result_links = (
            await auth_third_party_service.get_provider_external_links(
                name="Not_registered_provider"
            )
        )
        assert result_links is None

    async def test_create_new_user(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        await auth_third_party_service.create_new_user(
            username="TheNewestUser", provider=1
        )
        created = (
            await auth_third_party_service.user_repo.validate_user_by_username(
                username="TheNewestUser"
            )
        )
        assert created is True

        user = await auth_third_party_service.user_repo.get_user_by_username(
            username="TheNewestUser"
        )
        user_id = user.id
        await auth_third_party_service.user_repo.delete(user_id=user_id)
        deleted = (
            await auth_third_party_service.user_repo.validate_user_by_username(
                username="TheNewestUser"
            )
        )
        assert deleted is False

    async def test_create_new_user_already_exists(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        with pytest.raises(DuplicationError):
            await auth_third_party_service.create_new_user(
                username="TestClient", provider=1
            )

    async def test_create_new_persistent_grant(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
    ) -> None:
        service = auth_third_party_service
        third_party_oidc_request_model.state = STUB_STATE
        service.request_model = third_party_oidc_request_model
        await service.create_new_persistent_grant(
            username="TestClient", secret_code="TestClientSecretCode"
        )
        created = await service.persistent_grant_repo.exists(
            grant_data="TestClientSecretCode", grant_type="authorization_code"
        )
        assert created is True

        await service.persistent_grant_repo.delete(
            grant_data="TestClientSecretCode", grant_type="code"
        )
        deleted = await service.persistent_grant_repo.exists(
            grant_data="TestClientSecretCode", grant_type="code"
        )
        assert deleted is False

    async def test_create_provider_state(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        state_request_model: StateRequestModel,
    ) -> None:
        service = auth_third_party_service
        service.state_request_model = state_request_model
        await service.create_provider_state()
        created = await service.oidc_repo.validate_state(
            state=state_request_model.state
        )
        assert created is True

    async def test_create_provider_state_exists(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        state_request_model: StateRequestModel,
    ) -> None:
        service = auth_third_party_service
        service.state_request_model = state_request_model
        with pytest.raises(ThirdPartyStateDuplicationError):
            await service.create_provider_state()
        await service.oidc_repo.delete_state(state=state_request_model.state)
        deleted = await service.oidc_repo.validate_state(
            state=state_request_model.state
        )
        assert deleted is False

    async def test_update_redirect_url_with_params(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
    ) -> None:
        service = auth_third_party_service
        service.request_model = third_party_oidc_request_model
        expected_uri = (
            "https://www.google.com/?code=Secrete_code&state=test_state"
        )
        result_uri = await service._update_redirect_url_with_params(
            redirect_uri="https://www.google.com/", secret_code="Secrete_code"
        )

        assert result_uri == expected_uri

    async def test_update_redirect_url_without_request_model(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        service = auth_third_party_service
        result_uri = await service._update_redirect_url_with_params(
            redirect_uri="https://www.google.com/", secret_code="Secrete_code"
        )

        assert result_uri is None

    async def test_update_redirect_url_no_state(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
    ) -> None:
        service = auth_third_party_service
        third_party_oidc_request_model.state = None
        service.request_model = third_party_oidc_request_model
        expected_uri = "https://www.google.com/?code=Secrete_code"
        result_uri = await service._update_redirect_url_with_params(
            redirect_uri="https://www.google.com/", secret_code="Secrete_code"
        )

        assert result_uri == expected_uri

    async def test_parse_response_content_data(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        expected_password = "BestOfTheBest"
        expected_client_id = "tony_stark"
        expected_username = "IronMan"

        to_parse = "gcp-api%20IdentityServerApi&client_id=tony_stark&password=BestOfTheBest&username=IronMan"
        result = auth_third_party_service._parse_response_content(to_parse)
        assert result["client_id"] == expected_client_id
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_response_content_data_len_two(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        expected_password = "BestOfTheBest"
        expected_username = "IronMan"

        to_parse = "password=BestOfTheBest&username=IronMan"
        result = auth_third_party_service._parse_response_content(to_parse)
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_empty_response_content(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        expected: dict[str, Any] = {}
        to_parse = ""
        result = auth_third_party_service._parse_response_content(to_parse)
        assert result == expected

    async def test_parse_response_content_without_separator(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        expected = {"some_key": "key"}
        to_parse = "some_key=key"
        result = auth_third_party_service._parse_response_content(to_parse)
        assert result == expected

    async def test_parse_response_content_uri(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        to_parse = f"https://www.google.com/?code=blfpo4Bk3xXME5-lyYnyVNiy9wA5RmXPREhT2NERKG8&state={STUB_STATE}"
        result = auth_third_party_service._parse_response_content(to_parse)
        assert result["state"] == STUB_STATE

    async def test_get_github_redirect_uri_empty_request_model(
        self, auth_third_party_service: AuthThirdPartyOIDCService
    ) -> None:
        result_uri = await auth_third_party_service.get_github_redirect_uri(
            provider_name="github"
        )
        assert result_uri is None

    async def test_get_github_redirect_uri(
        self,
        auth_third_party_service: AuthThirdPartyOIDCService,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
        connection: AsyncSession,
        mocker: Any,
    ) -> None:
        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "NewUserNew"

        patch_start = "src.business_logic.services.third_party_oidc_service.AuthThirdPartyOIDCService"
        if not auth_third_party_service:
            raise AssertionError
        service = auth_third_party_service
        service.request_model = third_party_oidc_request_model
        service.request_model.state = STUB_STATE
        mocker.patch(
            f"{patch_start}.make_request_for_access_token", replace_post
        )
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="e6a4c6014f35f4acf016",
                provider_client_secret="645c46bd7604a12de37f26218445c8813db86d9a",
                enabled=True,
            )
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        expected_uri_start = "https://www.google.com/?code"
        expected_uri_end = STUB_STATE

        result_uri = await service.get_github_redirect_uri(
            provider_name="github"
        )
        assert result_uri
        assert result_uri.startswith(expected_uri_start)
        assert result_uri.endswith(expected_uri_end)
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 1,
                IdentityProviderMapped.provider_client_id
                == "e6a4c6014f35f4acf016",
                IdentityProviderMapped.provider_client_secret
                == "645c46bd7604a12de37f26218445c8813db86d9a",
            )
        )
        await connection.commit()

    async def test_make_post_request_for_access_token(
        self, auth_third_party_service: AuthThirdPartyOIDCService, mocker: Any
    ) -> None:
        service = auth_third_party_service
        request_params = {
            "client_id": "TestClient",
            "client_secret": "client_secret",
            "code": "code",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(
                200,
                content=b"access_token=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&scope=&token_type=bearer",
            ),
        )
        expected_token = "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"
        access_token = await service.make_request_for_access_token(
            method="POST",
            access_url="https://www.google.com/",
            params=request_params,
        )
        assert access_token == expected_token

    async def test_make_get_request_for_user_data(
        self, auth_third_party_service: AuthThirdPartyOIDCService, mocker: Any
    ) -> None:
        service = auth_third_party_service
        headers = {
            "Authorization": "Bearer " + "access_token",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(200, json={"login": "NewUser"}),
        )
        expected_user_name = "NewUser"
        user_name = await service.make_get_request_for_user_data(
            access_url="https://www.google.com/", headers=headers
        )
        assert user_name == expected_user_name


@pytest.mark.asyncio
class TestThirdPartyGoogleService:
    async def test_get_google_access_token(
        self, google_third_party_service: ThirdPartyGoogleService, mocker: Any
    ) -> None:
        service = google_third_party_service
        request_params = {
            "client_id": "TestClient",
            "client_secret": "client_secret",
            "code": "code",
            "grant_type": "authorization_code",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "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",
                    "token_type": "Bearer",
                },
            ),
        )
        expected_token = "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"
        access_token = await service.get_google_access_token(
            method="POST",
            access_url="https://www.google.com/",
            params=request_params,
        )
        assert access_token == expected_token

    async def test_make_get_request_for_user_email(
        self, google_third_party_service: ThirdPartyGoogleService, mocker: Any
    ) -> None:
        service = google_third_party_service
        headers = {
            "Authorization": "Bearer " + "access_token",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(
                200, json={"name": "NewUser", "email": "example@boo.com"}
            ),
        )
        expected_user_email = "example@boo.com"
        user_name = await service.make_get_request_for_user_email(
            access_url="https://www.google.com/", headers=headers
        )
        assert user_name == expected_user_email

    async def test_get_google_redirect_uri_empty_request_model(
        self, google_third_party_service: ThirdPartyGoogleService
    ) -> None:
        result_uri = await google_third_party_service.get_google_redirect_uri(
            provider_name="google"
        )
        assert result_uri is None

    async def test_get_google_redirect_uri(
        self,
        google_third_party_service: ThirdPartyGoogleService,
        third_party_google_request_model: ThirdPartyGoogleRequestModel,
        connection: AsyncSession,
        mocker: Any,
    ):
        async def replace_post(*args, **kwargs):
            return "access_token"

        async def replace_get(*args, **kwargs):
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGoogleService"

        service = google_third_party_service
        service.request_model = third_party_google_request_model
        service.request_model.state = STUB_STATE
        mocker.patch(f"{patch_start}.get_google_access_token", replace_post)
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_email", replace_get
        )

        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=3,
                provider_client_id="419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                provider_client_secret="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",
                enabled=True,
            )
        )
        await connection.commit()
        await connection.execute(
            insert(IdentityProviderState).values(state=STUB_STATE)
        )
        await connection.commit()
        expected_uri_start = "https://www.google.com/?code"
        expected_uri_end = STUB_STATE

        result_uri = await service.get_google_redirect_uri(
            provider_name="google"
        )

        assert result_uri.startswith(expected_uri_start)
        assert result_uri.endswith(expected_uri_end)
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 3,
                IdentityProviderMapped.provider_client_id
                == "419477723901-3tt7r3i0scubumglh5a7r8lmmff6k20g.apps.googleusercontent.com",
                IdentityProviderMapped.provider_client_secret
                == "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",
            )
        )
        await connection.commit()
