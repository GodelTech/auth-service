import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository

ANSWER_USER_INFO = {'sub': '1',
                    'name': 'Daniil',
                    'given_name': 'Ibragim',
                    'family_name': 'Krats',
                    'middle_name': '-el-',
                    'nickname': 'Nagibator2000',
                    'preferred_username': 'Graf',
                    'profile': 'werni_stenu',
                    'picture': 'https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg',
                    'website': 'https://www.instagram.com/daniilkrats/',
                    'email': 'danya.krats87@gmail.com',
                    'email_verified': True,
                    'gender': 'Attack Helicopter',
                    'birthdate': '02/01/2000',
                    'zoneinfo': 'GMT+1',
                    'locale': 'Warsaw',
                    'phone_number': '+48510143314',
                    'phone_number_verified': False,
                    'address': '5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania',
                    'updated_at': 1234567890,
                    }


class TestUserInfoEndpoint:

    @pytest.mark.asyncio
    async def test_successful_userinfo_request(self, user_info_service, client: AsyncClient):
        uis = user_info_service
        uis.client_id = "santa"
        token = await uis.jwt.encode_jwt(payload={"sub": 1})

        headers = {
            'authorization': token,
        }

        response = await client.request('GET', '/userinfo/', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        for key in ANSWER_USER_INFO:
            assert response_content[key] == ANSWER_USER_INFO[key]

    @pytest.mark.asyncio
    async def test_successful_userinfo_jwt(self, user_info_service, client: AsyncClient):
        uis = user_info_service
        uis.client_id = "santa"
        token = await uis.jwt.encode_jwt(payload={"sub": 1})

        headers = {
            'authorization': token,
            'accept': 'application/json'
        }
        uis.authorization = token

        response = await client.request('GET', '/userinfo/jwt', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        response_content = await uis.jwt.decode_token(token=response_content)
        answer = {k: ANSWER_USER_INFO[k] for k in ANSWER_USER_INFO.keys()}
        answer["email_verified"] = 'true'
        answer["phone_number_verified"] = 'false'
        answer["updated_at"] = str(answer["updated_at"])

        assert response_content == answer

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_incorrect_token(
            self,
            user_info_service,
            client: AsyncClient
    ):
        uis = user_info_service
        uis.client_id = "santa"
        secret = await uis.client_repo.get_client_secrete_by_client_id(client_id=uis.client_id)
        token = await uis.jwt.encode_jwt(payload={"blablabla": "blablabla"})

        for url in ('/userinfo/', '/userinfo/jwt'):
            params = {
                'authorization': token,
            }
            response = await client.request('GET', url, headers=params)
            response_content = json.loads(response.content.decode('utf-8'))
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response_content == {'detail': "Incorrect Token"}

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_user_without_claims(
            self,
            user_info_service,
            client: AsyncClient
    ):
        uis = user_info_service
        uis.client_id = "santa"
        token = await uis.jwt.encode_jwt(payload={"sub": "2"})

        for url in ('/userinfo/', '/userinfo/jwt'):
            headers = {
                'authorization': token,
            }

            response = await client.request('GET', url, headers=headers)

            assert response.status_code == status.HTTP_403_FORBIDDEN

            response_content = json.loads(response.content.decode('utf-8'))
            assert response_content == {"detail": "You don't have permission for this claims"}
