import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete

from src.data_access.postgresql.tables.users import UserClaim
from src.business_logic.services.jwt_token import JWTService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine


scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)

TOKEN_HINT_DATA = {"sub": 8, "client_id": "spider_man", "type": "code"}


@pytest.mark.asyncio
class TestAuthorizationTokenFlow:
    async def test_successful_authorization_token_flow(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # 1st stage Authorization endpoint creates record with secrete code in Persistent grant table
        params = {
            "client_id": "spider_man",
            "response_type": "token",
            "scope": "openid profile",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        content_type = "application/x-www-form-urlencoded"
        response = await client.request(
            "POST",
            "/authorize/",
            data=params
            | {"username": "PeterParker", "password": "the_beginner"},
            headers={"Content-Type": content_type},
        )
        data = response.headers["location"].split("?")[1]
        access_token = {
            item.split("=")[0]: item.split("=")[1] for item in data.split("&")
        }["access_token"]
        assert response.status_code == status.HTTP_302_FOUND

        # There is no 2nd stage Token endpoint. Token is formed in the Authorization endpoint method POST

        # 3rd stage UserInfo endpoint retrieves user data from UserClaims table
        await connection.execute(
            insert(UserClaim).values(
                user_id=8, claim_type_id=1, claim_value="Peter"
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

        # 4th stage EndSession. The logout happens on the application side.
        # Since there are no grants stored we check for status.HTTP_404_NOT_FOUND and relevant message
        jwt_service = JWTService()

        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://garza-taylor.com/",
            "state": "test_state",
        }
        expected_content = '{"message":"You are not logged in"}'
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_successful_authorization_token_id_token_flow(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # 1st stage Authorization endpoint creates record with secrete code in Persistent grant table
        params = {
            "client_id": "spider_man",
            "response_type": "id_token token",
            "scope": "openid profile",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        content_type = "application/x-www-form-urlencoded"
        response = await client.request(
            "POST",
            "/authorize/",
            data=params
            | {"username": "TestClient", "password": "test_password"},
            headers={"Content-Type": content_type},
        )
        data = response.headers["location"].split("?")[1]
        access_token = {
            item.split("=")[0]: item.split("=")[1] for item in data.split("&")
        }["access_token"]
        assert response.status_code == status.HTTP_302_FOUND

        # There is no 2nd stage Token endpoint. Tokens are formed in the Authorization endpoint method POST

        # 3rd stage UserInfo endpoint retrieves user data from UserClaims table
        await connection.execute(
            insert(UserClaim).values(
                user_id=8, claim_type_id=1, claim_value="Peter"
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

        # 4th stage EndSession. The logout happens on the application side.
        # Since there are no grants stored we check for status.HTTP_404_NOT_FOUND and relevant message
        jwt_service = JWTService()

        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://garza-taylor.com/",
            "state": "test_state",
        }
        expected_content = '{"message":"You are not logged in"}'
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
