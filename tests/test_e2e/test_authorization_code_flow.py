import base64
import hashlib
import os

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_access.postgresql.tables.users import User, UserClaim

scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)

TOKEN_HINT_DATA = {"sub": None, "client_id": "spider_man", "type": "code"}


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestAuthorizationCodeFlow:
    async def test_successful_authorization_code_flow(
        self, client: AsyncClient, connection: AsyncSession
    ) -> None:
        # Stage 1: Authorization endpoint creates a record with a secret code in the Persistent Grant table
        authorization_params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        authorization_response = await client.request(
            "GET", "/authorize/", params=authorization_params
        )
        assert authorization_response.status_code == status.HTTP_200_OK

        user_credentials = {
            "username": "PeterParker",
            "password": "the_beginner",
        }
        response = await client.request(
            "POST",
            "/authorize/",
            data={**authorization_params, **user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_302_FOUND

        # Stage 2: Token endpoint changes the secret code in the Persistent Grant table to a token
        secret_code = response.headers["location"].split("=")[1]

        token_params = {
            "client_id": "test_client",
            "grant_type": "authorization_code",
            "code": secret_code,
            "redirect_uri": "https://www.google.com/",
        }
        token_response = await client.request(
            "POST",
            "/token/",
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response_data = token_response.json()
        access_token = response_data.get("access_token")
        id_token = response_data.get("id_token")
        assert token_response.status_code == status.HTTP_200_OK

        # Stage 3: UserInfo endpoint retrieves user data from UserClaims table
        user_id_query = select(User.id).where(User.username == "TestClient")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()

        user_claim_insertion = insert(UserClaim).values(
            user_id=user_id, claim_type_id=1, claim_value="Peter"
        )
        await connection.execute(user_claim_insertion)
        await connection.commit()

        user_info_response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )
        assert user_info_response.status_code == status.HTTP_200_OK

        # Stage 4: EndSession endpoint deletes all records in the Persistent Grant table for the corresponding user
        logout_params = {"id_token_hint": id_token}
        end_session_response = await client.request(
            "GET", "/endsession/", params=logout_params
        )
        assert end_session_response.status_code == status.HTTP_302_FOUND


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestAuthorizationCodeFlowWithPKCE:
    # https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce
    async def test_successful_s256(
        self,
        client: AsyncClient,
        connection: AsyncSession,
    ):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def get_verifier_and_challenge() -> tuple[str, str]:
            verifier = (
                base64.urlsafe_b64encode(os.urandom(32))
                .decode("utf-8")
                .rstrip("=")
            )
            verifier = verifier[
                :128
            ]  # Ensuring it doesn't exceed the maximum length
            challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
            challenge = (
                base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
            )
            return verifier, challenge

        code_verifier, code_challenge = get_verifier_and_challenge()

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

        user_id_query = select(User.id).where(User.username == "PeterParker")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()

        # Prepare data for the next stage
        await connection.execute(
            insert(UserClaim).values(
                user_id=user_id, claim_type_id=1, claim_value="Peter"
            )
        )
        await connection.commit()

        # 10. Your application can use the access token to call an API to access information about the user.
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )

        # 11. The API responds with requested data.
        data = response.json()
        assert data == {"sub": str(user_id)}

    async def test_successful_plain(
        self, client: AsyncClient, connection: AsyncSession
    ):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def get_verifier_and_challenge() -> tuple[str, str]:
            verifier = (
                base64.urlsafe_b64encode(os.urandom(32))
                .decode("utf-8")
                .rstrip("=")
            )
            verifier = verifier[
                :128
            ]  # Ensuring it doesn't exceed the maximum length
            challenge = verifier
            return verifier, challenge

        code_verifier, code_challenge = get_verifier_and_challenge()

        # 3. Auth0's SDK redirects the user to the Auth0 Authorization Server (`/authorize` endpoint)
        # along with the `code_challenge`.
        params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "code_challenge": code_challenge,
            "code_challenge_method": "plain",
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

        user_id_query = select(User.id).where(User.username == "PeterParker")
        user_id = (await connection.execute(user_id_query)).scalar_one_or_none()

        # Prepare data for the next stage
        await connection.execute(
            insert(UserClaim).values(
                user_id=user_id, claim_type_id=1, claim_value="Peter"
            )
        )
        await connection.commit()

        # 10. Your application can use the access token to call an API to access information about the user.
        response = await client.request(
            "GET", "/userinfo/", headers={"authorization": access_token}
        )

        # 11. The API responds with requested data.
        data = response.json()
        assert data == {"sub": str(user_id)}

    async def test_unsuccessful_s256(self, client: AsyncClient):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def get_verifier_and_challenge() -> tuple[str, str]:
            verifier = (
                base64.urlsafe_b64encode(os.urandom(32))
                .decode("utf-8")
                .rstrip("=")
            )
            verifier = verifier[
                :128
            ]  # Ensuring it doesn't exceed the maximum length
            challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
            challenge = (
                base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
            )
            return verifier, challenge

        code_verifier, code_challenge = get_verifier_and_challenge()

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

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_unsuccessful_plain(self, client: AsyncClient):
        # 1. The user clicks Login within the application.
        # 2. Auth0's SDK creates a cryptographically-random `code_verifier` and from this generates a `code_challenge`.
        def get_verifier_and_challenge() -> tuple[str, str]:
            verifier = (
                base64.urlsafe_b64encode(os.urandom(32))
                .decode("utf-8")
                .rstrip("=")
            )
            verifier = verifier[
                :128
            ]  # Ensuring it doesn't exceed the maximum length
            challenge = verifier
            return verifier, challenge

        code_verifier, code_challenge = get_verifier_and_challenge()

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

        assert response.status_code == status.HTTP_400_BAD_REQUEST
