import jwt
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from tests.test_unit.fixtures import end_session_request_model, TOKEN_HINT_DATA, TokenHint


@pytest.mark.asyncio
class TestEndSessionEndpoint:

    async def test_successful_authorize_request(
            self,
            engine,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        service = end_session_service
        service.request_model = end_session_request_model
        secret = await service.client_repo.get_client_secrete_by_client_id(client_id=TOKEN_HINT_DATA["client_id"])
        token = await service.jwt_service.encode_jwt(secret=secret, payload={})
        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            grant = await session.execute(
                insert(PersistentGrant).values(
                    key="test_key",
                    client_id=TOKEN_HINT_DATA["client_id"],
                    subject_id=TOKEN_HINT_DATA["sub"],
                    data=TOKEN_HINT_DATA["data"],
                    type=TOKEN_HINT_DATA["type"],
                    expiration=False
                )
            )
            await session.commit()
            hint = TokenHint()
            token_hint = await hint.get_token_hint()
            params = {
                "id_token_hint": token_hint,
                "post_logout_redirect_uri": "http://www.jones.com/",
                "state": "test_state",
            }
            response = await client.request("GET", "/endsession/", params=params)
            assert response.status_code == status.HTTP_302_FOUND

            await session.execute(
                delete(PersistentGrant).where(PersistentGrant.client_id == TOKEN_HINT_DATA["client_id"])
            )
            await session.commit()

    async def test_successful_authorize_request_without_uri(
            self,
            engine,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        service = end_session_service
        service.request_model = end_session_request_model
        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            grant = await session.execute(
                insert(PersistentGrant).values(
                    key="test_key",
                    client_id=TOKEN_HINT_DATA["client_id"],
                    subject_id=TOKEN_HINT_DATA["sub"],
                    data=TOKEN_HINT_DATA["data"],
                    type=TOKEN_HINT_DATA["type"],
                    expiration=False
                )
            )
            await session.commit()

        hint = TokenHint()
        token_hint = await hint.get_token_hint()

        params = {"id_token_hint": token_hint}
        response = await client.request("GET", "/endsession/", params=params)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_successful_authorize_request_wrong_uri(
            self,
            engine,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        service = end_session_service
        service.request_model = end_session_request_model
        session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            grant = await session.execute(
                insert(PersistentGrant).values(
                    key="test_key",
                    client_id=TOKEN_HINT_DATA["client_id"],
                    subject_id=TOKEN_HINT_DATA["sub"],
                    data=TOKEN_HINT_DATA["data"],
                    type=TOKEN_HINT_DATA["type"],
                    expiration=False
                )
            )
            await session.commit()

        hint = TokenHint()
        token_hint = await hint.get_token_hint()
        params = {
            "id_token_hint": token_hint,
            "post_logout_redirect_uri": "some_uri",
        }
        expected_content = '{"message":"Bad post logout redirect uri"}'
        response = await client.request("GET", "/endsession/", params=params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_end_session_bad_token(
            self,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        service = end_session_service
        service.request_model = end_session_request_model
        expected_content = '{"message":"Bad id_token_hint"}'
        params = {
            "id_token_hint": "id_token_hint",
            "post_logout_redirect_uri": "some_uri",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_end_session_not_full_token(
            self,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        hint = TokenHint()
        short_token_hint = await hint.get_short_token_hint()
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.id_token_hint = short_token_hint

        expected_content = '{"message":"The id_token_hint is missing something"}'
        params = {
            "id_token_hint": short_token_hint,
            "post_logout_redirect_uri": "http://www.jones.com/",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content

    async def test_end_session_no_persistent_grant(
            self,
            client: AsyncClient,
            end_session_service,
            end_session_request_model
    ):
        hint = TokenHint()
        token_hint = await hint.get_token_hint()
        service = end_session_service
        service.request_model = end_session_request_model
        expected_content = '{"message":"You are not logged in"}'
        params = {
            "id_token_hint": token_hint,
            "post_logout_redirect_uri": "http://www.jones.com/",
        }
        response = await client.request("GET", "/endsession/", params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.content.decode("UTF-8") == expected_content
