from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.identity_resource import (
    IdentityProviderMapped,
    IdentityProviderState,
)
from src.data_access.postgresql.tables.users import User, UserClaim


STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!spider_man!_!http://127.0.0.1:8888/callback/"


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestThirdPartyGoogleFlow:
    async def test_successful_google_code_flow(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        # Stage 1: Authorization endpoint with get request
        authorization_params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }
        authorization_response = await client.request(
            "GET", "/authorize/", params=authorization_params
        )
        assert authorization_response.status_code == status.HTTP_200_OK

        # Stage 2: Third party Google provider endpoint request to collect username and access_token
        provider_state_insertion = insert(IdentityProviderState).values(
            state=STUB_STATE
        )
        provider_mapped_insertion = insert(IdentityProviderMapped).values(
            identity_provider_id=1,
            provider_client_id="e6a4c6014f35f4acf016",
            provider_client_secret="***REMOVED***",
            enabled=True,
        )
        await connection.execute(provider_state_insertion)
        await connection.execute(provider_mapped_insertion)
        await connection.commit()

        async def replace_post(*args: Any, **kwargs: Any) -> str:
            return "access_token"

        async def replace_get(*args: Any, **kwargs: Any) -> str:
            return "NewUserNew"

        patch_start = "src.business_logic.third_party_auth.service_impls.google.GoogleAuthService"
        mocker.patch(f"{patch_start}._get_access_token", replace_post)
        mocker.patch(f"{patch_start}._get_username", replace_get)
        google_params = {"code": "test_code", "state": STUB_STATE}
        google_response = await client.request(
            "GET", "/authorize/oidc/google", params=google_params
        )
        assert google_response.status_code == status.HTTP_302_FOUND

        # Stage 3: Token endpoint changes secrete code in Persistent Grant table to token
        secret_code = (
            google_response.headers["location"].split("=")[1].split("&")[0]
        )
        token_params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": secret_code,
            "scope": "test",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }
        token_response = await client.request(
            "POST",
            "/token/",
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response_data = token_response.json()
        access_token = response_data.get("access_token")
        assert token_response.status_code == status.HTTP_200_OK

        # Stage 4: UserInfo endpoint retrieves user data from UserClaims table
        user_id_query = select(User.id).where(User.username == "NewUserNew")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()
        user_claim_insertion = insert(UserClaim).values(
            user_id=user_id, claim_type_id=1, claim_value="Peter"
        )
        await connection.execute(user_claim_insertion)
        await connection.commit()
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert response.status_code == status.HTTP_200_OK

        # Stage 5: EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
        jwt_service = JWTService()
        token_hint_data = {
            "sub": user_id,
            "client_id": "spider_man",
            "type": "code",
        }

        id_token_hint = await jwt_service.encode_jwt(payload=token_hint_data)

        logout_params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://www.sparks.net/",
            "state": "test_state",
        }
        end_session_response = await client.request(
            "GET", "/endsession/", params=logout_params
        )
        assert end_session_response.status_code == status.HTTP_302_FOUND
