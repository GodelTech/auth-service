import datetime
import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete

from src.data_access.postgresql.tables.persistent_grant import PersistentGrant

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


async def create_persistent_grant_instance(service, token, subject_id):
    uis = service
    persistent_grant = {
        "key": "unique_key",
        "client_id": uis.client_id,
        "data": token,
        "subject_id": subject_id,
        "type": "access_token",
    }
    await uis.persistent_grant_repo.session.execute(
        insert(PersistentGrant).values(**persistent_grant)
    )
    await uis.persistent_grant_repo.session.commit()


async def clean_persistent_grant(service, client_id):
    uis = service
    await uis.persistent_grant_repo.session.execute(
        delete(PersistentGrant).
        where(PersistentGrant.client_id == client_id)
    )
    await uis.persistent_grant_repo.session.commit()


class TestUserInfoEndpoint:

    @pytest.mark.asyncio
    async def test_successful_userinfo_request(self, user_info_service, client: AsyncClient):

        uis = user_info_service
        uis.jwt.set_expire_time(expire_hours=1)
        uis.client_id = "santa"
        secret = await uis.client_repo.get_client_secrete_by_client_id(client_id=uis.client_id)
        token = await uis.jwt.encode_jwt(secret=secret, payload=ANSWER_USER_INFO)

        await create_persistent_grant_instance(service=uis, token=token, subject_id=3)

        headers = {
            'authorization': token,
        }
        response = await client.request('GET', '/userinfo/', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        for key in ANSWER_USER_INFO:
            assert response_content[key] == ANSWER_USER_INFO[key]

        await clean_persistent_grant(service=uis, client_id=uis.client_id)

    @pytest.mark.asyncio
    async def test_successful_userinfo_jwt(self, user_info_service, client: AsyncClient):

        uis = user_info_service
        uis.jwt.set_expire_time(expire_hours=1)
        uis.client_id = "krampus"
        secret = await uis.client_repo.get_client_secrete_by_client_id(client_id=uis.client_id)

        token = await uis.jwt.encode_jwt(secret=secret, payload=ANSWER_USER_INFO)

        persistent_grant = {
            "key": "unique_key",
            "client_id": uis.client_id,
            "data": token,
            "subject_id": 4,
            "type": "access_token",
        }
        await uis.persistent_grant_repo.session.execute(
            insert(PersistentGrant).values(**persistent_grant)
        )
        await uis.persistent_grant_repo.session.commit()

        headers = {
            'authorization': token,
        }
        uis.authorization = token

        response = await client.request('GET', '/userinfo/jwt', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        response_content = await uis.jwt.decode_token(secret=secret, token=response_content)
        answer = {k: ANSWER_USER_INFO[k] for k in ANSWER_USER_INFO.keys()}
        answer["email_verified"] = 'true'
        answer["phone_number_verified"] = 'false'
        answer["updated_at"] = str(answer["updated_at"])

        assert response_content == answer
        await uis.persistent_grant_repo.session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == "krampus")
            )

        await uis.persistent_grant_repo.session.commit()

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_incorrect_token(self, user_info_service, client: AsyncClient):
        uis = user_info_service
        uis.jwt.set_expire_time(expire_hours=1)
        uis.client_id = "santa"
        secret = await uis.client_repo.get_client_secrete_by_client_id(client_id=uis.client_id)
        token = await uis.jwt.encode_jwt(secret=secret, payload={"blablabla": "blablabla"})

        await create_persistent_grant_instance(service=uis, token=token, subject_id=3)

        for url in ('/userinfo/', '/userinfo/jwt'):
            params = {
                'authorization': token,
            }
            response = await client.request('GET', url, headers=params)
            response_content = json.loads(response.content.decode('utf-8'))
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response_content == {'detail': "Incorrect Token"}

        await clean_persistent_grant(service=uis, client_id=uis.client_id)

    @pytest.mark.asyncio
    async def test_userinfo_and_userinfo_jwt_request_with_user_without_claims(self, user_info_service, client: AsyncClient):
        uis = user_info_service
        uis.jwt.set_expire_time(expire_hours=1)
        uis.client_id = "santa"
        secret = await uis.client_repo.get_client_secrete_by_client_id(client_id=uis.client_id)
        token = await uis.jwt.encode_jwt(secret=secret, payload={"sub": "3"})

        await create_persistent_grant_instance(service=uis, token=token, subject_id=3)

        for url in ('/userinfo/', '/userinfo/jwt'):
            headers = {
                'authorization': token,
            }

            await uis.persistent_grant_repo.create(
                client_id="santa", data=token, user_id=3
            )

            response = await client.request('GET', url, headers=headers)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

            response_content = json.loads(response.content.decode('utf-8'))
            assert response_content == {"detail": "Claims for user you are looking for does not exist"}

        await clean_persistent_grant(service=uis, client_id=uis.client_id)
