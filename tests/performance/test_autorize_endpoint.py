# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncEngine
from locust import TaskSet, HttpUser, task, between


class TaskSetAuthorizeEndpointGET(TaskSet):

    def on_start(self):
        self.params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        self.wrong_params = {
            "client_id": "wrong_test_client",
            "response_type": "wrong_code",
            "scope": "wrong_openid",
            "redirect_uri": "wrong_https://www.google.com/",
        }

    @task(5)
    def test_successful_authorize_request(self) -> None:

        self.client.request("GET", "/authorize/", params=self.params,
                            name="/authorize/")

    @task
    def test_unsuccessful_authorize_request_wrong_data(self) -> None:

        self.client.request("GET", "/authorize/", params=self.wrong_params,
                            name="/authorize/")


class TaskSetAuthorizeEndpointPOST(TaskSet):
    content_type = "application/x-www-form-urlencoded"

    def on_start(self):
        self.params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }
        self.wrong_params = {
            "response_type": "wrong_code",
            "scope": "wrong_openid",
            "redirect_uri": "wrong_https://www.google.com/",
        }

    @task(5)
    def test_successful_authorize_request(self) -> None:

        self.client.request(
            "POST",
            "/authorize/",
            data=self.params,
            headers={"Content-Type": self.content_type},
            name="/authorize/"
        )

    @task
    def test_unsuccessful_authorize_request(self) -> None:
        self.client.request(
            "POST",
            "/authorize/",
            data=self.wrong_params,
            headers={"Content-Type": self.content_type},
            name="/authorize/"
        )