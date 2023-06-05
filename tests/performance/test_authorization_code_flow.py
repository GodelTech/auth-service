import asyncio

import pytest
import logging
from urllib import parse
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from importlib import import_module
from locust import TaskSet, SequentialTaskSet, HttpUser, task, between

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.users import User, UserClaim
from tests.conftest import connection

scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=spider_man&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "the_beginner&username=PeterParker"
)

# TOKEN_HINT_DATA = {"sub": None, "client_id": "spider_man", "type": "code"}


class TaskSetAuthorizationCodeFlow(SequentialTaskSet):

    def on_start(self):
        self.authorization_params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": "https://www.google.com/",
        }
        self.user_credentials = {"username": "PeterParker", "password": "the_beginner"}

   # client: AsyncClient, connection: AsyncSession
    @task
    def test_successful_authorization_GET(self) -> None:
        # Stage 1: Authorization endpoint creates a record with a secret code in the Persistent Grant table
        self.authorization_response = self.client.request("GET", "/authorize/",
                                                          params=self.authorization_params,
                                                          name="1/authorize/  secret_code flow")
        # logging.info(f"test_successful_authorization_GET; response.status_code: {self.authorization_response.status_code}")
        # assert self.authorization_response.status_code == status.HTTP_200_OK

    @task
    def test_successful_authorization_POST(self):
        self.response_post = self.client.request(
            "POST",
            "/authorize/",
            data={**self.authorization_params, **self.user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="2/authorize/  secret_code flow"
        )
        # logging.info(f"test_obtain_access_token; self.response_post.url: {self.response_post.url}")
        # logging.info(f"test_successful_authorization_POST; response.status_code _302_: {self.response_post.status_code}")
        # assert self.response_post.status_code == status.HTTP_302_FOUND

    ######### ERROR status_code 200, NO head with return url and "location" ########
    @task
    def test_obtain_access_token(self):
        # Stage 2: Token endpoint changes the secret code in the Persistent Grant table to a token
        # logging.info(f"test_obtain_access_token; self.response_post: {self.response_post}!!!!!!")
        # logging.info(f"test_obtain_access_token; self.response_post.headers: {self.response_post.headers}!!!!!!")
        # logging.info(f"test_obtain_access_token; self.response_post.url: {self.response_post.url}")
        # self.secret_code = self.response.headers["location"].split("=")[1]
        # logging.info(f"test_obtain_access_token; self.response_post.url: {self.response_post.url}")
        self.secret_code = self._get_code(url=self.response_post.url)
        # logging.info(f"test_obtain_access_token; self.secret_code: {self.secret_code}")
        self.token_params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": self.secret_code,
            "redirect_uri": "https://www.google.com/",
        }
        self.token_response = self.client.request(
            "POST",
            "/token/",
            data=self.token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="3/token/ secret_code flow"
        )
        self.response_data = self.token_response.json()
        self.access_token = self.response_data.get("access_token")
        logging.info(f"test_obtain_access_token; self.access_token; {self.access_token}")
        # logging.info(f"test_obtain_access_token; sself.token_response.status_code; {self.token_response.status_code}")
        # assert self.token_response.status_code == status.HTTP_200_OK

    def _get_code(self, url):
        # logging.info(f"_get_code(self, url); url: {url}")
        self.parsed_url = parse.urlparse(url)
        self.query_parameters = parse.parse_qs(self.parsed_url.query)
        self.continue_url = self.query_parameters.get("continue", [None])[0]
        # logging.info(f"_get_code; if 'continue_url' is not None:; self.response.url: {self.response.url}")
        if self.continue_url is not None:
            self.continue_url_decoded = parse.unquote(self.continue_url)
            self.code_url = parse.urlparse(self.continue_url_decoded)
            self.code_parameters = parse.parse_qs(self.code_url.query)
            self.secret_code = self.code_parameters.get("code", [None])[0]
            return self.secret_code
        else:
            # logging.info(f"if self.continue_url is None; _get_code(self, url); url: {url}")
            self.secret_code = self.response_post.url.split("=")[1]
            return self.secret_code

        # # Stage 3: UserInfo endpoint retrieves user data from UserClaims table
        # # ?????????????????? ##
        # user_id_query = select(User.id).where(User.username == "PeterParker")
        # user_id = (await connection.execute(user_id_query)).scalar_one_or_none()
        #
        # user_claim_insertion = insert(UserClaim).values(user_id=user_id, claim_type_id=1, claim_value="Peter")
        # await connection.execute(user_claim_insertion)
        # await connection.commit()
        # ##### ----------------------- ##############
        #
    # @task
    # def test_userinfo_GET(self):
    #
    #     self.user_info_response = self.client.request(
    #         "GET", "/userinfo/", headers={"authorization": self.access_token},
    #         name="4/userinfo/"
    #     )
    #
    #     logging.info(f"test_userinfo_GET; self.user_info_response.json(): {self.user_info_response.json()}")
    #     self.user_id = self.user_info_response["user_id"]
    #     logging.info(f"test_userinfo_GET; self.user_id: {self.user_id}")
    #     # assert self.user_info_response.status_code == status.HTTP_200_OK
    #
    #     # ?????????????????? ##
    #     # Stage 4: EndSession endpoint deletes all records in the Persistent Grant table for the corresponding user


    # @task
    # def test_end_session(self):
    #     self.id_token_hint = asyncio.run(self._get_id_token_hint())
    #
    #     self.logout_params = {
    #         "id_token_hint": self.id_token_hint,
    #         "post_logout_redirect_uri": "http://www.sparks.net/",
    #         "state": "test_state",
    #     }
    #     self.end_session_response = self.client.request("GET", "/endsession/",
    #                                                     params=self.logout_params,
    #                                                     name="5/endsession/")
    #
    #     logging.info(f"test_end_session; self.end_session_response.status_code: {self.end_session_response.status_code}")
    #     assert self.end_session_response.status_code == status.HTTP_302_FOUND

    # async def _get_id_token_hint(self, connection=connection):
    #     self.user_id_query = select(User.id).where(User.username == "PeterParker")
    #     self.user_id = (await connection.execute(self.user_id_query)).scalar_one_or_none()
    #
    #     self.user_claim_insertion = insert(UserClaim).values(user_id=self.user_id, claim_type_id=1, claim_value="Peter")
    #     await connection.execute(self.user_claim_insertion)
    #     await connection.commit()
    #     # user_id_query = select(User.id).where(User.username == "PeterParker")
    #     # user_id = (await connection.execute(user_id_query)).scalar_one_or_none()
    #     self.jwt_token = import_module('src.business_logic.services.jwt_token')
    #     self.jwt_service = self.jwt_token.JWTService()
    #
    #     self.TOKEN_HINT_DATA = {"sub": None, "client_id": "spider_man", "type": "code"}
    #     self.TOKEN_HINT_DATA["sub"] = self.user_id
    #
    #     self.id_token_hint = await self.jwt_service.encode_jwt(payload=self.TOKEN_HINT_DATA)
    #     return self.id_token_hint
