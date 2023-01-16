import json
import mock
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.userinfo import UserInfoServies
from src.business_logic.services.tokens import TokenService
from src.data_access.postgresql.repositories.user import UserRepository

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

async def new_check_authorisation_token(*args, **kwargs):
    return True

class TestUserInfoEndpoint:

    @pytest.mark.asyncio
    async def test_successful_userinfo_request(connection: AsyncSession, client: AsyncClient):

        with mock.patch.object(
            TokenService, "check_authorisation_token", new=new_check_authorisation_token
        ):
            uis = UserInfoServies()
            uis.jwt.set_expire_time(expire_hours=1)
            
            headers = {
                'authorization': uis.jwt.encode_jwt(payload = {"sub":"1"}),
            }
            response = await client.request('GET', '/userinfo/', headers=headers)

            assert response.status_code == status.HTTP_200_OK
            response_content = json.loads(response.content.decode('utf-8'))
            for key in ANSWER_USER_INFO:
                assert response_content[key] == ANSWER_USER_INFO[key]


    @pytest.mark.asyncio
    async def test_successful_userinfo_jwt(connection: AsyncSession, client: AsyncClient):
        with mock.patch.object(
            TokenService, "check_authorisation_token", new=new_check_authorisation_token
        ):
            uis = UserInfoServies()
            uis.jwt.set_expire_time(expire_hours=1)
            token = uis.jwt.encode_jwt(payload = {"sub":"1"})

            headers = {
                'authorization': token,
            }
            response = await client.request('GET', '/userinfo/jwt', headers=headers)

            assert response.status_code == status.HTTP_200_OK
            response_content = json.loads(response.content.decode('utf-8'))
            response_content = uis.jwt.decode_token(response_content)
            answer = {k : ANSWER_USER_INFO[k] for k in ANSWER_USER_INFO.keys()}
            answer["email_verified"] = 'true'
            answer["phone_number_verified"] = 'false'
            answer["updated_at"] = str(answer["updated_at"])
            assert response_content == answer

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_incorect_token(connection: AsyncSession, client: AsyncClient):

        uis = UserInfoServies()
        uis.jwt.set_expire_time(expire_hours=1)

        for url in ('/userinfo/', '/userinfo/jwt'):
            token = uis.jwt.encode_jwt(payload={"blablabla": "blablabla"})
            params = {
                'authorization': token,
            }
            response = await client.request('GET', url, params=params)
            response_content = json.loads(response.content.decode('utf-8'))
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response_content == {'detail': 'Incorrect Authorization Token'} 


    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_user_without_claims(connection: AsyncSession, client: AsyncClient):

        async def new_execute_empty(*args, **kwargs):
            return ()
        with mock.patch.object(
            TokenService, "check_authorisation_token", new=new_check_authorisation_token
        ):
            uis = UserInfoServies()
            uis.jwt.set_expire_time(expire_hours=1)

            for url in ('/userinfo/', '/userinfo/jwt'):

                with mock.patch.object(UserRepository, "request_DB_for_claims", new=new_execute_empty):
                    headers = {
                        'authorization': uis.jwt.encode_jwt(payload = {"sub":"1"}),
                    }
                    response = await client.request('GET', url, headers=headers)

                    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

                    response_content = json.loads(response.content.decode('utf-8'))
                    assert response_content == {"detail": "Claims for user you are looking for does not exist"}
