import httpx
import pytest
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.tables import IdentityProviderMapped
from src.data_access.postgresql.tables.identity_resource import (
    IdentityProviderState,
)
from tests.test_unit.fixtures import (
    third_party_oidc_request_model,
    third_party_microsoft_request_model
)
from src.business_logic.services import (
    ThirdPartyGitLabService,
    ThirdPartyMicrosoftService,
)
from typing import Any
from src.presentation.api.models import (
    ThirdPartyOIDCRequestModel,
    ThirdPartyMicrosoftRequestModel,
)

STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"


@pytest.mark.asyncio
class TestGitlabService:

    async def test_gitlab_make_request_for_access_token(
        self, gitlab_third_party_service: ThirdPartyGitLabService, mocker: Any
    ) -> None:
        service = gitlab_third_party_service
        request_params = {
            "client_id": "TestClient",
            "client_secret": "client_secret",
            "redirect_uri": "redirect_uri",
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
        access_token = await service.make_request_for_access_token(
            method="POST",
            access_url="https://www.google.com/",
            params=request_params,
        )
        assert access_token == expected_token

    async def test_gitlab_make_get_request_for_user_data(
        self, gitlab_third_party_service: ThirdPartyGitLabService, mocker: Any
    ) -> None:
        service = gitlab_third_party_service
        headers = {
            "Authorization": "Bearer " + "access_token",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(200, json={"nickname": "NewUser"}),
        )
        expected_user_nickname = "NewUser"
        user_nickname = await service.make_get_request_for_user_data(
            access_url="https://www.google.com/", headers=headers
        )
        assert user_nickname == expected_user_nickname

    async def test_gitlab_get_redirect_uri_no_model(
        self, gitlab_third_party_service: ThirdPartyGitLabService
    ) -> None:
        result_uri = await gitlab_third_party_service.get_redirect_uri(
            provider_name="gitlab"
        )
        assert result_uri is None

    async def test_gitlab_get_redirect_uri(
        self,
        gitlab_third_party_service: ThirdPartyGitLabService,
        third_party_oidc_request_model: ThirdPartyOIDCRequestModel,
        connection: AsyncSession,
        mocker: Any,
    ):
        async def replace_post(*args, **kwargs):
            return "access_token"

        async def replace_get(*args, **kwargs):
            return "UserNewNickname"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyGitLabService"

        service = gitlab_third_party_service
        service.request_model = third_party_oidc_request_model
        service.request_model.state = STUB_STATE
        mocker.patch(f"{patch_start}.make_request_for_access_token", replace_post)
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=5,
                provider_client_id="b93c44acd8904c4881ca2d64686c46c3ecf0efbe579b7df25e9b49fe59d2bea5",
                provider_client_secret="7f632a34656e624330f4f36c2cb30c6593d674b59f246dee1cf520ec89d5e5e6",
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

        result_uri = await service.get_redirect_uri(
            provider_name="gitlab"
        )

        assert result_uri.startswith(expected_uri_start)
        assert result_uri.endswith(expected_uri_end)
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 5,
                IdentityProviderMapped.provider_client_id
                == "b93c44acd8904c4881ca2d64686c46c3ecf0efbe579b7df25e9b49fe59d2bea5",
                IdentityProviderMapped.provider_client_secret
                == "7f632a34656e624330f4f36c2cb30c6593d674b59f246dee1cf520ec89d5e5e6",
            )
        )
        await connection.commit()


@pytest.mark.asyncio
class TestMicrosoftService:

    async def test_microsoft_make_request_for_access_token(
        self, microsoft_third_party_service: ThirdPartyMicrosoftService, mocker: Any

    ) -> None:
        service = microsoft_third_party_service
        request_params = {
            "client_id": "TestClient",
            "client_secret": "client_secret",
            "redirect_uri": "redirect_uri",
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
        access_token = await service.make_request_for_access_token(
            method="POST",
            access_url="https://www.google.com/",
            params=request_params,
        )
        assert access_token == expected_token

    async def test_microsoft_make_get_request_for_user_data(
        self, microsoft_third_party_service: ThirdPartyMicrosoftService, mocker: Any
    ) -> None:
        service = microsoft_third_party_service
        headers = {
            "Authorization": "Bearer " + "access_token",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        mocker.patch(
            "src.business_logic.services.third_party_oidc_service.AsyncClient.request",
            return_value=httpx.Response(200, json={"email": "NewUserEmail"}),
        )
        expected_user_email = "NewUserEmail"
        user_email = await service.make_get_request_for_user_data(
            access_url="https://www.google.com/", headers=headers
        )
        assert user_email == expected_user_email

    async def test_microsoft_get_redirect_uri_no_model(
        self, microsoft_third_party_service: ThirdPartyMicrosoftService
    ) -> None:
        result_uri = await microsoft_third_party_service.get_redirect_uri(
            provider_name="microsoft"
        )
        assert result_uri is None

    async def test_microsoft_get_redirect_uri(
        self,
        microsoft_third_party_service: ThirdPartyMicrosoftService,
        third_party_microsoft_request_model: ThirdPartyMicrosoftRequestModel,
        connection: AsyncSession,
        mocker: Any,
    ):
        async def replace_post(*args, **kwargs):
            return "access_token"

        async def replace_get(*args, **kwargs):
            return "UserNewEmail"

        patch_start = "src.business_logic.services.third_party_oidc_service.ThirdPartyMicrosoftService"

        service = microsoft_third_party_service
        service.request_model = third_party_microsoft_request_model
        service.request_model.state = STUB_STATE
        mocker.patch(f"{patch_start}.make_request_for_access_token", replace_post)
        mocker.patch(
            f"{patch_start}.make_get_request_for_user_data", replace_get
        )

        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=6,
                provider_client_id="80e0019e-b47c-40b8-bad5-413f15fafdf0",
                provider_client_secret="5_e8Q~oGsgilQM-TofukM.HRPyiChks_lGsNwbpD",
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

        result_uri = await service.get_redirect_uri(
            provider_name="microsoft"
        )

        assert result_uri.startswith(expected_uri_start)
        assert result_uri.endswith(expected_uri_end)
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.identity_provider_id == 6,
                IdentityProviderMapped.provider_client_id
                == "80e0019e-b47c-40b8-bad5-413f15fafdf0",
                IdentityProviderMapped.provider_client_secret
                == "5_e8Q~oGsgilQM-TofukM.HRPyiChks_lGsNwbpD",
            )
        )
        await connection.commit()
