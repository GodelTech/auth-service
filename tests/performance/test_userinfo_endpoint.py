import asyncio
import json
import logging

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from locust import TaskSet, SequentialTaskSet, task

from src.data_access.postgresql.repositories import ClientRepository, UserRepository
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services import UserInfoServices
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from tests.conftest import user_info_service, client, connection

# ANSWER_USER_INFO = {
#                     'name': 'Daniil',
#                     'given_name': 'Ibragim',
#                     'family_name': 'Krats',
#                     'middle_name': '-el-',
#                     'nickname': 'Nagibator2000',
#                     'preferred_username': 'Graf',
#                     'profile': 'werni_stenu',
#                     'picture': 'https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg',
#                     'website': 'https://www.instagram.com/daniilkrats/',
#                     'gender': 'Attack Helicopter',
#                     'birthdate': '02/01/2000',
#                     'zoneinfo': 'GMT+1',
#                     'locale': 'Warsaw',
#                     'phone_number': '+48510143314',
#                     'phone_number_verified': "false",
#                     'address': '5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania',
#                     'updated_at': "1234567890",
#                     }


class TaskSetInfoEndpoint(SequentialTaskSet):

    def on_start(self):
        self.params_get = {
            "client_id": "test_client",
            "grant_type": "client_credentials",
            "client_secret": "past",
        }
        self.response_keys = self.client.request(
            "POST",
            "/token/",
            data=self.params_get,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.response_content = json.loads(self.response_keys.content.decode("utf-8"))
        self.access_token = self.response_content.get("access_token")
        logging.info(f"self.access_token: {self.access_token}")

    # async def _get_header(
    #         self,
    #         user_info_service: UserInfoServices = user_info_service,
    #         client: AsyncClient = client,
    #         session: AsyncSession = connection
    # ) -> None:
    #     self.user_info_service = UserInfoServices(
    #     session=session,
    #     jwt=JWTService(),
    #     client_repo=ClientRepository(session=session),
    #     persistent_grant_repo=PersistentGrantRepository(session=session),
    #     user_repo=UserRepository(session=session),
    # )
    #     self.token = await self.user_info_service.jwt.encode_jwt(payload={"sub": 1,  'scope': 'profile', "aud":["userinfo"]})
    #     self.headers = {
    #         "authorization": self.token,
    #     }
    #     logging.info(f"!!!!self.token: {self.token}")
    #     return self.headers

    @task
    def test_successful_userinfo_get(self) -> None:
        # jwt = JWTService()
        # token = await jwt.encode_jwt(payload={"sub": 1, 'scope': 'profile', "aud":["userinfo"]})
        self.headers = {
            "authorization": "Bearer " + self.access_token,
        }
        # self.headers = asyncio.run(self._get_header())
        self.response = self.client.request("GET", "/userinfo/", headers=self.headers)
        # self.response_content = json.loads(self.response.content.decode("utf-8"))

        logging.info(f"self.response.status_code: {self.response.status_code}")
        # assert self.response.status_code == status.HTTP_200_OK
        # assert response_content == ANSWER_USER_INFO

    # @task
    # def test_successful_userinfo_jwt_get(self) -> None:
    #     # token = await user_info_service.jwt.encode_jwt(payload={"sub": 1, 'scope': 'profile', "aud":["userinfo"]})
    #     self.headers = {"authorization": self.access_token, "accept": "application/json"}
    #     # user_info_service.authorization = token            # ?????
    #     self.response_jwt = self.client.request(
    #         "GET", "/userinfo/jwt", headers=self.headers
    #     )
    #     assert self.response_jwt.status_code == status.HTTP_200_OK
    #
    #     # response_content = json.loads(response.content.decode("utf-8"))
    #     # response_content = await user_info_service.jwt.decode_token(
    #     #     token=response_content
    #     # )
    #     # assert response_content == ANSWER_USER_INFO
    #
    # @task
    # def test_successful_userinfo_post(self) -> None:    # !! only for tests. Dont need !!
    #     # token = await user_info_service.jwt.encode_jwt(payload={"sub": 1,  'scope': 'profile', "aud":["userinfo"]})
    #     self.headers = {
    #         "authorization": self.access_token,
    #     }
    #     response = self.client.request("POST", "/userinfo/", headers=self.headers)
    #     # response_content = json.loads(response.content.decode("utf-8"))
    #     assert response.status_code == status.HTTP_200_OK
    #     # for key in ANSWER_USER_INFO:
    #     #     expected_value = ANSWER_USER_INFO[key].lower()
    #     #     actual_value = str(response_content[key]).lower()
    #     #     assert actual_value == expected_value