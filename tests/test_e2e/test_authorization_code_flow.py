import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, insert, delete, text

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.tables.users import UserClaim
from src.business_logic.services.jwt_token import JWTService


scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)

TOKEN_HINT_DATA = {"sub": 8, "client_id": "spider_man", "type": "code"}


@pytest.mark.asyncio
class TestAuthorizationCodeFlow:
    async def test_successful_authorization_code_flow(
        self, client: AsyncClient, connection
    ):

        # 1st stage Authorization endpoint creates record with secrete code in Persistent grant table
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        content_type = "application/x-www-form-urlencoded"
        response = await client.request(
            "POST",
            "/authorize/",
            data=params,
            headers={"Content-Type": content_type},
        )
        assert response.status_code == status.HTTP_302_FOUND

        # 2nd stage Token endpoint changes secrete code in Persistent grant table to token
        secret_code = await connection.execute(
            select(PersistentGrant.grant_data)
            .where(PersistentGrant.client_id == 8)
            # .where(PersistentGrant.client_id == "spider_man")
        )

        secret_code = secret_code.first()[0]

        params = {
            "client_id": "spider_man",
            "grant_type": "code",
            "code": secret_code,
            "scope": "test",
            "redirect_uri": "https://www.arnold-mann.net/",
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

        # 3rd stage UserInfo endpoint retrieves user data from UserClaims table

        # The sequence id number is out of sync and raises duplicate key error
        # We manually bring it back in sync
        await connection.execute(
            text("SELECT setval(pg_get_serial_sequence('user_claims', 'id'), (SELECT MAX(id) FROM user_claims)+1);")
        )

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

        # 4th stage EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
        jwt_service = JWTService()

        id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

        params = {
            "id_token_hint": id_token_hint,
            "post_logout_redirect_uri": "http://www.avery.com/",
            "state": "test_state",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_302_FOUND
