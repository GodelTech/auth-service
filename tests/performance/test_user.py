import pytest
from fastapi import status
from httpx import AsyncClient
from src.data_access.postgresql.repositories.user import UserRepository
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from locust import TaskSet, SequentialTaskSet, task


logger = logging.getLogger(__name__)


class TaskSetUserEndpoint(SequentialTaskSet):

    def on_start(self):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.data_first = {
            "username": "polnareff",
            "email": "polnareff@mail",
            "password": "polnareff",
            "picture": "polnareff",
            "website": "polnareff",
            "gender": "polnareff",
        }
        self.data_second = {
            "name":"polnareff",
            "given_name":"polnareff",
            "family_name":"polnareff",
            "middle_name":"polnareff",
            }

    @task
    def test_successful_get_HTML_register_profile(self) -> None:
        self.client.request(
            "GET", "/user/register/profile", headers=self.headers,
            name="1/user/register/scope"
        )
        # assert response.status_code == status.HTTP_200_OK
        # response_content = response.content.decode("utf-8")
        # assert "<h1>Registration Form</h1>" in response_content
        # assert '<input type="text" id="name" name="name" required>' in response_content

    # @task
    # def test_successful_get_HTML_register_openid(self) -> None:
    #     self.client.request(
    #         "GET", "/user/register/openid", headers=self.headers,
    #         name="2/user/register/scope"
    #     )
    #     # assert response.status_code == status.HTTP_200_OK
    #     # response_content = response.content.decode("utf-8")
    #     # assert "<h1>Registration Form</h1>" in response_content
    #     # assert '<input type="text" id="name" name="name" required>' not in response_content

    @task
    def test_successful_register_post(self) -> None:
        self.headers_a = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.data_a = {
            "username": "polnareff",
            "email": "polnareff@mail",
            "password": "polnareff",
            "picture": "polnareff",
            "website": "polnareff",
            "gender": "polnareff",
        }
        self.client.request(
            "POST", "/user/register", headers=self.headers_a, data=self.data_a,
            name="2/user/register"
        )

        # self.client.request(
        #     "POST", "/user/register", headers=self.headers, data=self.data_first,
        #     name="2/user/register"
        # )
        # assert response.status_code == status.HTTP_200_OK
        # response_content = response.content.decode("utf-8")
        # user_repo = UserRepository(connection)
        # user = await user_repo.get_user_by_username("polnareff")
        # assert '<h1>Success</h1>' in response_content
    @task
    def test_successful_add_info_get(self) -> None:
        self.client.request(
            "GET", "/user/add_info/polnareff?scope=profile",
            headers=self.headers,
            data=self.data_first,
            name="3/user/add_info/polnareff?scope=profile"
        )
        # assert response.status_code == status.HTTP_200_OK
        # response_content = response.content.decode("utf-8")
        # assert "<h1>We need to know something else</h1>" in response_content

    @task
    def test_successful_add_info_post(self) -> None:
        self.client.request(
            "POST", "/user/add_info/polnareff",
            headers=self.headers,
            data=self.data_second,
            name="4/user/add_info/polnareff"
        )
        # assert response.status_code == status.HTTP_200_OK
        # claims = await user_repo.get_claims(user.id)
        # assert "family_name" in claims.keys()



        