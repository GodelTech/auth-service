import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, insert, delete, text

from src.data_access.postgresql.tables.identity_resource import (
    IdentityProviderState,
    IdentityProviderMapped,
)
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.tables.users import UserClaim, User
from src.business_logic.services.jwt_token import JWTService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)
STUB_STATE = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!spider_man!_!https://www.google.com/"


@pytest.mark.asyncio
class TestThirdPartyGitLabFlow:
    async def test_successful_gitlab_code_flow(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        # 1st stage Authorization endpoint with get request
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        # 2nd stage third party GitHub provider endpoint
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

        params = {"code": "test_code", "state": STUB_STATE}
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

        # 3nd stage Token endpoint changes secrete code in Persistent grant table to token (application side)
        user_id = await connection.execute(
            select(User.id).where(User.username == "UserNewNickname")
        )
        user_id = user_id.first()[0]
        secret_code = await connection.execute(
            select(PersistentGrant.grant_data).where(
                PersistentGrant.client_id == 8,
                PersistentGrant.user_id == user_id,
            )
        )

        secret_code = secret_code.first()[0]

        params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": secret_code,
            "scope": "test",
            "redirect_uri": "https://www.google.com/",
        }

        content_type = "application/x-www-form-urlencoded"
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": content_type},
        )
        response_data = response.json()
        access_token = response_data.get("access_token")

        assert response.status_code == status.HTTP_200_OK

        # 4th stage UserInfo endpoint retrieves user data from UserClaims table

        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('user_claims', 'id'), (SELECT MAX(id) FROM user_claims)+1);"
            )
        )
        await connection.execute(
            insert(UserClaim).values(
                user_id=user_id, claim_type_id=1, claim_value="Peter"
            )
        )
        await connection.commit()
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert response.status_code == status.HTTP_200_OK
        await connection.execute(
            delete(UserClaim)
            .where(UserClaim.user_id == 8)
            .where(UserClaim.claim_type_id == 1)
        )
        await connection.commit()

        # 5th stage EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
        jwt_service = JWTService()
        token_hint_data = {
            "sub": user_id,
            "client_id": "spider_man",
            "type": "code",
        }

        id_token_hint = await jwt_service.encode_jwt(payload=token_hint_data)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://www.sparks.net/",
            "state": "test_state",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.asyncio
class TestThirdPartyMicrosoftFlow:
    async def test_successful_microsoft_code_flow(
        self, client: AsyncClient, connection: AsyncSession, mocker: Any
    ) -> None:
        # 1st stage Authorization endpoint with get request
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        # 2nd stage third party GitHub provider endpoint
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

        params = {"code": "test_code", "state": STUB_STATE}
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

        # 3nd stage Token endpoint changes secrete code in Persistent grant table to token (application side)
        user_id = await connection.execute(
            select(User.id).where(User.username == "UserNewEmail")
        )
        user_id = user_id.first()[0]
        secret_code = await connection.execute(
            select(PersistentGrant.grant_data).where(
                PersistentGrant.client_id == 8,
                PersistentGrant.user_id == user_id,
            )
        )

        secret_code = secret_code.first()[0]

        params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": secret_code,
            "scope": "test",
            "redirect_uri": "https://www.google.com/",
        }

        content_type = "application/x-www-form-urlencoded"
        response = await client.request(
            "POST",
            "/token/",
            data=params,
            headers={"Content-Type": content_type},
        )
        response_data = response.json()
        access_token = response_data.get("access_token")

        assert response.status_code == status.HTTP_200_OK

        # 4th stage UserInfo endpoint retrieves user data from UserClaims table

        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('user_claims', 'id'), (SELECT MAX(id) FROM user_claims)+1);"
            )
        )
        await connection.execute(
            insert(UserClaim).values(
                user_id=user_id, claim_type_id=1, claim_value="Peter"
            )
        )
        await connection.commit()
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert response.status_code == status.HTTP_200_OK
        await connection.execute(
            delete(UserClaim)
            .where(UserClaim.user_id == 8)
            .where(UserClaim.claim_type_id == 1)
        )
        await connection.commit()

        # 5th stage EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
        jwt_service = JWTService()
        token_hint_data = {
            "sub": user_id,
            "client_id": "spider_man",
            "type": "code",
        }

        id_token_hint = await jwt_service.encode_jwt(payload=token_hint_data)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://www.sparks.net/",
            "state": "test_state",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_302_FOUND
