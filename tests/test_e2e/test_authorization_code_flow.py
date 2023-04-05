import base64
import hashlib
import os
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, insert, delete, text

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
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


# @pytest.mark.asyncio
# class TestAuthorizationCodeFlow:
#     async def test_successful_authorization_code_flow(
#         self, client: AsyncClient, connection: AsyncSession
#     ) -> None:
#         # 1st stage Authorization endpoint creates record with secrete code in Persistent grant table
#         params = {
#             "client_id": "spider_man",
#             "response_type": "code",
#             "scope": "openid profile",
#             "redirect_uri": "https://www.google.com/",
#         }
#         response = await client.request("GET", "/authorize/", params=params)
#         assert response.status_code == status.HTTP_200_OK

#         content_type = "application/x-www-form-urlencoded"
#         response = await client.request(
#             "POST",
#             "/authorize/",
#             data=params
#             | {"username": "PeterParker", "password": "the_beginner"},
#             headers={"Content-Type": content_type},
#         )
#         assert response.status_code == status.HTTP_302_FOUND

#         # 2nd stage Token endpoint changes secrete code in Persistent grant table to token
#         secret_code = await connection.execute(
#             select(PersistentGrant.grant_data).where(
#                 PersistentGrant.client_id == 8
#             )
#         )

#         secret_code = secret_code.first()[0]

#         params = {
#             "client_id": "spider_man",
#             "grant_type": "authorization_code",
#             "code": secret_code,
#             "redirect_uri": "https://www.google.com/",
#         }

#         content_type = "application/x-www-form-urlencoded"

#         response = await client.request(
#             "POST",
#             "/token/",
#             data=params,
#             headers={"Content-Type": content_type},
#         )
#         response_data = response.json()
#         access_token = response_data.get("access_token")
#         assert response.status_code == status.HTTP_200_OK

#         # 3rd stage UserInfo endpoint retrieves user data from UserClaims table

#         # The sequence id number is out of sync and raises duplicate key error
#         # We manually bring it back in sync
#         await connection.execute(
#             text(
#                 "SELECT setval(pg_get_serial_sequence('user_claims', 'id'), (SELECT MAX(id) FROM user_claims)+1);"
#             )
#         )

#         await connection.execute(
#             insert(UserClaim).values(
#                 user_id=8, claim_type_id=1, claim_value="Peter"
#             )
#         )
#         await connection.commit()
#         response = await client.request(
#             "GET", "/userinfo/", headers={"authorization": access_token}
#         )
#         assert response.status_code == status.HTTP_200_OK
#         await connection.execute(
#             delete(UserClaim)
#             .where(UserClaim.user_id == 8)
#             .where(UserClaim.claim_type_id == 1)
#         )
#         await connection.commit()

#         # 4th stage EndSession endpoint deletes all records in the Persistent grant table for the corresponding user
#         jwt_service = JWTService()

#         id_token_hint = await jwt_service.encode_jwt(payload=TOKEN_HINT_DATA)

#         params = {
#             "id_token_hint": id_token_hint,
#             "post_logout_redirect_uri": "http://www.sparks.net/",
#             "state": "test_state",
#         }
#         response = await client.request("GET", "/endsession/", params=params)
#         assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.asyncio
class TestAuthorizationCodeFlowWithPKCE:
    # https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce
    async def test_successful(
        self, client: AsyncClient, connection: AsyncSession
    ):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def base64_urlencode(data):
            data = base64.urlsafe_b64encode(data).rstrip(b"=")
            return data.decode("utf-8")

        code_verifier = base64_urlencode(os.urandom(32))
        code_challenge = base64_urlencode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        )

        # 3. Auth0's SDK redirects the user to the Auth0 Authorization Server (`/authorize` endpoint)
        # along with the `code_challenge`.
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        # 4. Your Auth0 Authorization Server redirects the user to the login and authorization prompt.
        # 5. The user authenticates using one of the configured login options
        # and may see a consent page listing the permissions Auth0 will give to the application.
        response = await client.request(
            "POST",
            "/authorize/",
            data=params
            | {"username": "PeterParker", "password": "the_beginner"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 6. Your Auth0 Authorization Server stores the `code_challenge`
        # and redirects the user back to the application with an authorization `code`, which is good for one use.
        from urllib.parse import urlparse, parse_qs

        assert response.status_code == status.HTTP_302_FOUND
        url = response.headers["location"]
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        code = query.get("code", [None])[0]

        # 7. Auth0's SDK sends this `code` and the `code_verifier` (created in step 2)
        # to the Auth0 Authorization Server (`/oauth/token` endpoint).
        response = await client.request(
            "POST",
            "/token/",
            data={
                "client_id": "spider_man",
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": "https://www.google.com/",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 8. Your Auth0 Authorization Server verifies the `code_challenge` and `code_verifier`.
        # 9. Your Auth0 Authorization Server responds with an ID token and access token (and optionally, a refresh token).
        response_data = response.json()
        access_token = response_data.get("access_token")
        assert response.status_code == status.HTTP_200_OK

        # Prepare data for the next stage
        await connection.execute(
            insert(UserClaim).values(
                user_id=8, claim_type_id=1, claim_value="Peter"
            )
        )
        await connection.commit()

        # 10. Your application can use the access token to call an API to access information about the user.
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )

        # 11. The API responds with requested data.
        data = response.json()
        assert data == {"sub": "8"}

    async def test_auth_request_fails_with_invalid_code_verifier(
        self, client: AsyncClient, connection: AsyncSession
    ):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def base64_urlencode(data):
            data = base64.urlsafe_b64encode(data).rstrip(b"=")
            return data.decode("utf-8")

        code_verifier = base64_urlencode(os.urandom(32))
        code_challenge = base64_urlencode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        )

        # 3. Auth0's SDK redirects the user to the Auth0 Authorization Server (`/authorize` endpoint)
        # along with the `code_challenge`.
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": "https://www.google.com/",
        }
        response = await client.request("GET", "/authorize/", params=params)
        assert response.status_code == status.HTTP_200_OK

        # 4. Your Auth0 Authorization Server redirects the user to the login and authorization prompt.
        # 5. The user authenticates using one of the configured login options
        # and may see a consent page listing the permissions Auth0 will give to the application.
        response = await client.request(
            "POST",
            "/authorize/",
            data=params
            | {"username": "PeterParker", "password": "the_beginner"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 6. Your Auth0 Authorization Server stores the `code_challenge`
        # and redirects the user back to the application with an authorization `code`, which is good for one use.
        from urllib.parse import urlparse, parse_qs

        assert response.status_code == status.HTTP_302_FOUND
        url = response.headers["location"]
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        code = query.get("code", [None])[0]

        # 7. Authorization Code Interception Attack
        # https://www.rfc-editor.org/rfc/rfc7636#page-4
        response = await client.request(
            "POST",
            "/token/",
            data={
                "client_id": "spider_man",
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": "INVALID_CODE_VERIFIER",
                "redirect_uri": "https://www.google.com/",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert len(response) == 0
