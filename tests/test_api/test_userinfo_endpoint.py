import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services import UserInfoServices
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository

ANSWER_USER_INFO = {
                    'name': 'Daniil',
                    'given_name': 'Ibragim',
                    'family_name': 'Krats',
                    'middle_name': '-el-',
                    'nickname': 'Nagibator2000',
                    'preferred_username': 'Graf',
                    'profile': 'werni_stenu',
                    'picture': 'https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg',
                    'website': 'https://www.instagram.com/daniilkrats/',
                    'gender': 'Attack Helicopter',
                    'birthdate': '02/01/2000',
                    'zoneinfo': 'GMT+1',
                    'locale': 'Warsaw',
                    'phone_number': '+48510143314',
                    'phone_number_verified': "false",
                    'address': '5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania',
                    'updated_at': "1234567890",
                    }


class TestUserInfoEndpoint:
    @pytest.mark.asyncio
    async def test_successful_userinfo_get_request(
        self, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        jwt = JWTService()
        token = await jwt.encode_jwt(payload={"sub": 1, 'scope': 'profile', "aud":["userinfo"]})
        headers = {
            "authorization": token,
        }
        response = await client.request("GET", "/userinfo/", headers=headers)
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_200_OK
        assert response_content == ANSWER_USER_INFO

    @pytest.mark.asyncio
    async def test_successful_userinfo_jwt_get_request(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(payload={"sub": 1, 'scope': 'profile', "aud":["userinfo"]})
        headers = {"authorization": token, "accept": "application/json"}
        user_info_service.authorization = token
        response = await client.request(
            "GET", "/userinfo/jwt", headers=headers
        )
        response_content = json.loads(response.content.decode("utf-8"))
        response_content = await user_info_service.jwt.decode_token(
            token=response_content
        )

        assert response.status_code == status.HTTP_200_OK
        assert response_content == ANSWER_USER_INFO

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_get_requests_with_incorrect_token(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(
            payload={"blablabla": "blablabla", "aud":["userinfo"]}
        )
        for url in ("/userinfo/", "/userinfo/jwt"):
            headers = {
                "authorization": token,
            }
            response = await client.request("GET", url, headers=headers)
            response_content = json.loads(response.content.decode("utf-8"))

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_get_requests_with_user_without_claims(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(payload={"sub": "2", "aud":["userinfo"]})
        for url in ("/userinfo/", "/userinfo/jwt"):
            headers = {
                "authorization": token,
            }
            response = await client.request("GET", url, headers=headers)
            response_content = json.loads(response.content.decode("utf-8"))

            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response_content == {
                "detail": "You don't have permission for this claims"
            }

    @pytest.mark.asyncio
    async def test_successful_userinfo_post_request(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(payload={"sub": 1,  'scope': 'profile', "aud":["userinfo"]})
        headers = {
            "authorization": token,
        }
        response = await client.request("POST", "/userinfo/", headers=headers)
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_200_OK
        for key in ANSWER_USER_INFO:
            expected_value = ANSWER_USER_INFO[key].lower()
            actual_value = str(response_content[key]).lower()
            assert actual_value == expected_value

    @pytest.mark.asyncio
    async def test_userinfo_post_request_with_incorrect_token(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(
            payload={"blablabla": "blablabla", "aud":["userinfo"]}
        )
        headers = {"authorization": token}
        response = await client.request("POST", "/userinfo/", headers=headers)
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_userinfo_post_request_with_user_without_claims(
        self, user_info_service: UserInfoServices, client: AsyncClient, engine: AsyncEngine,
    ) -> None:
        token = await user_info_service.jwt.encode_jwt(payload={"sub": "2", "aud":["userinfo"]})
        headers = {
            "authorization": token,
        }
        response = await client.request("POST", "/userinfo/", headers=headers)
        response_content = json.loads(response.content.decode("utf-8"))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response_content == {
            "detail": "You don't have permission for this claims"
        }
