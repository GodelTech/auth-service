import json

import mock
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.userinfo import UserInfoServies
from src.data_access.postgresql.repositories.user import UserRepository

# class ClaimTypeMock:
#     def __init__(self, code) -> None:
#         self.code = code

# class ClaimMock:
#     def __init__(self, claim_value, claim_type) -> None:
#         self.claim_value = claim_value
#         self.claim_type = ClaimTypeMock(code=claim_type)


# DB_ANSWER = (
#     {"UserClaim": ClaimMock(claim_type="name", claim_value="Daniil")},
#     {"UserClaim": ClaimMock(claim_type="given_name", claim_value="Ibragim")},
#     {"UserClaim": ClaimMock(claim_type="family_name", claim_value="Krats")},
#     {"UserClaim": ClaimMock(claim_type="middle_name", claim_value="-el-")},
#     {"UserClaim": ClaimMock(claim_type="nickname",
#                             claim_value="Nagibator2000")},
#     {"UserClaim": ClaimMock(
#         claim_type="preferred_username", claim_value="Graf")},
#     {"UserClaim": ClaimMock(claim_type="profile", claim_value="werni_stenu")},
#     {"UserClaim": ClaimMock(
#         claim_type="picture", claim_value="https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg")},
#     {"UserClaim": ClaimMock(
#         claim_type="website", claim_value="https://www.instagram.com/daniilkrats/")},
#     {"UserClaim": ClaimMock(
#         claim_type="email", claim_value="danya.krats87@gmail.com")},
#     {"UserClaim": ClaimMock(claim_type="email_verified", claim_value=True)},
#     {"UserClaim": ClaimMock(claim_type="gender",
#                             claim_value="Attack Helicopter")},
#     {"UserClaim": ClaimMock(claim_type="birthdate", claim_value="02/01/2000")},
#     {"UserClaim": ClaimMock(claim_type="zoneinfo", claim_value="GMT+1")},
#     {"UserClaim": ClaimMock(claim_type="locale", claim_value="Warsaw")},
#     {"UserClaim": ClaimMock(claim_type="phone_number",
#                             claim_value="+48510143314")},
#     {"UserClaim": ClaimMock(
#         claim_type="phone_number_verified", claim_value=False)},
#     {"UserClaim": ClaimMock(
#         claim_type="address", claim_value="5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania")},
#     {"UserClaim": ClaimMock(claim_type="updated_at", claim_value=1234567890)}
# )

# ANSWER_USER_INFO = {'sub': '1',
#                     'name': 'Daniil',
#                     'given_name': 'Ibragim',
#                     'family_name': 'Krats',
#                     'middle_name': '-el-',
#                     'nickname': 'Nagibator2000',
#                     'preferred_username': 'Graf',
#                     'profile': 'werni_stenu',
#                     'picture': 'https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg',
#                     'website': 'https://www.instagram.com/daniilkrats/',
#                     'email': 'danya.krats87@gmail.com',
#                     'email_verified': True,
#                     'gender': 'Attack Helicopter',
#                     'birthdate': '02/01/2000',
#                     'zoneinfo': 'GMT+1',
#                     'locale': 'Warsaw',
#                     'phone_number': '+48510143314',
#                     'phone_number_verified': False,
#                     'address': '5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania',
#                     'updated_at': 1234567890,
#                     }


# @pytest.mark.asyncio
# async def test_successful_userinfo_request(connection: AsyncSession, client: AsyncClient):

#     async def new_execute_dict(*args, **kwargs):
#         return DB_ANSWER

#     uis = UserInfoServies()
#     uis.jwt.set_expire_time(expire_hours=1)
#     with mock.patch.object(UserRepository, "request_DB_for_claims", new=new_execute_dict):
#         params = {
#             'authorization': uis.jwt.encode_jwt(payload = {"sub":"1"}),
#         }
#         response = await client.request('GET', '/userinfo/', params=params)

#         assert response.status_code == status.HTTP_200_OK
#         response_content = json.loads(response.content.decode('utf-8'))
#         for key in ANSWER_USER_INFO:
#             assert response_content[key] == ANSWER_USER_INFO[key]


# @pytest.mark.asyncio
# async def test_successful_userinfo_jwt(connection: AsyncSession, client: AsyncClient):

#     async def new_execute_dict(*args, **kwargs):
#         return DB_ANSWER

#     uis = UserInfoServies()
#     uis.jwt.set_expire_time(expire_hours=1)
#     token = uis.jwt.encode_jwt(payload = {"sub":"1"})

#     with mock.patch.object(UserRepository, "request_DB_for_claims", new=new_execute_dict):
#         params = {
#             'authorization': token,
#         }
#         response = await client.request('GET', '/userinfo/jwt', params=params)

#         assert response.status_code == status.HTTP_200_OK
#         response_content = json.loads(response.content.decode('utf-8'))
#         sub = str(uis.jwt.decode_token(token)['sub'])
#         assert response_content == uis.jwt.encode_jwt(
#             payload={'sub': sub} | ANSWER_USER_INFO, include_expire= False)


# @pytest.mark.asyncio
# async def test_userinfo_and_userinfo_jwt_request_with_incorect_token(connection: AsyncSession, client: AsyncClient):

#     uis = UserInfoServies()
#     uis.jwt.set_expire_time(expire_hours=1)

#     for url in ('/userinfo/', '/userinfo/jwt'):
#         token = uis.jwt.encode_jwt(payload={"blablabla": "blablabla"})
#         params = {
#             'authorization': token,
#         }
#         response = await client.request('GET', url, params=params)
#         response_content = json.loads(response.content.decode('utf-8'))
#         assert response.status_code == status.HTTP_403_FORBIDDEN
#         assert response_content == {"detail": "Incorrect Token"}


# @pytest.mark.asyncio
# async def test_userinfo_and_userinfo_jwt_request_with_user_without_claims(connection: AsyncSession, client: AsyncClient):

#     async def new_execute_empty(*args, **kwargs):
#         return ()

#     uis = UserInfoServies()
#     uis.jwt.set_expire_time(expire_hours=1)

#     for url in ('/userinfo/', '/userinfo/jwt'):

#         with mock.patch.object(UserRepository, "request_DB_for_claims", new=new_execute_empty):
#             params = {
#                 'authorization': uis.jwt.encode_jwt(payload = {"sub":"1"}),
#             }
#             response = await client.request('GET', url, params=params)

#             assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#             response_content = json.loads(response.content.decode('utf-8'))
#             assert response_content == {"detail": "Claims for user you are looking for does not exist"}
