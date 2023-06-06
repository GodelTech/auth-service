import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
import json
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.users import User, UserClaim

scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)

TOKEN_HINT_DATA = {"sub": None, "client_id": "spider_man", "type": "code"}


@pytest.mark.asyncio
class TestAuthorizationCodeFlow:

    async def test_successful_authorization_code_flow(
            self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # Stage 1: Authorization endpoint creates a record with a secret code in the Persistent Grant table
        authorization_params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": "http://127.0.0.1:8888/callback/",
        }
        authorization_response = await client.request("GET", "/authorize/", params=authorization_params)
        assert authorization_response.status_code == status.HTTP_200_OK

        user_credentials = {"username": "PeterParker", "password": "the_beginner"}
        response = await client.request(
            "POST",
            "/authorize/",
            data={**authorization_params, **user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Stage 2: Token endpoint changes the secret code in the Persistent Grant table to a token
        secret_code = json.load(response)['redirect_url']
        secret_code = secret_code.split('=')[1]

        token_params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": secret_code,
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

        # Stage 3: UserInfo endpoint retrieves user data from UserClaims table
        user_id_query = select(User.id).where(User.username == "PeterParker")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()

        user_claim_insertion = insert(UserClaim).values(user_id=user_id, claim_type_id=1, claim_value="Peter")
        await connection.execute(user_claim_insertion)
        await connection.commit()

        user_info_response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert user_info_response.status_code == status.HTTP_200_OK

        # Stage 4: EndSession endpoint deletes all records in the Persistent Grant table for the corresponding user
        jwt_service = JWTService()

        TOKEN_HINT_DATA["sub"] = user_id

        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

        logout_params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://www.sparks.net/",
            "state": "test_state",
        }
        end_session_response = await client.request("GET", "/endsession/", params=logout_params)
        assert end_session_response.status_code == status.HTTP_302_FOUND
