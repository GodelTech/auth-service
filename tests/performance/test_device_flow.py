import logging

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from locust import TaskSet, SequentialTaskSet, HttpUser, task, between

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables import User, UserClaim
from src.data_access.postgresql.tables.device import Device


class TaskSetDeviceFlow(SequentialTaskSet):
    content_type = "application/x-www-form-urlencoded"

    @task
    def test_successful_device_POST(self) -> None:
        # Stage 1: Client requests a device code
        self.request_params = {"client_id": "test_client",
                          "scope": "openid"}
        self.response = self.client.request("POST", "/device/", data=self.request_params,
                                        headers={"Content-Type": self.content_type},
                                        name="1/device/")
        self.response_data = self.response.json()
        self.device_code = self.response_data.get("device_code")
        self.user_code = self.response_data.get("user_code")
        # assert self.response.status_code == status.HTTP_200_OK
        # assert self.device_code is not None
        # assert self.user_code is not None

        # Stage 2: User navigates to the device login form and checks the user_code
    @task
    def test_successful_device_auth_GET(self):
        self.response = self.client.request("GET", "/device/auth", name="2/device/auth")
        # assert self.response.status_code == status.HTTP_200_OK

    @task
    def test_successful_device_auth_POST(self):
        self.response = self.client.request("POST", "/device/auth", data={"user_code": self.user_code},
                                        headers={"Content-Type": self.content_type},
                                        name="3/device/auth")
        # logging.info(f"test_successful_device_auth_POST; self.response.status_code: {self.response.status_code}")
        # assert self.response.status_code == status.HTTP_302_FOUND

    @task
    def test_get_device_login_confirm(self) -> None:
        self.client.request("GET", "/device/auth/success",
                     name="4/device/auth/success")

    @task
    def test_get_device_cancel(self) -> None:
        self.client.request("GET", "/device/auth/cancel",
                            name="5/device/auth/cancel")

    @task
    def test_user_authorization_form(self):
        # Stage 3: Client requests user authorization (usually done by redirecting the user to an authorization form)
        self.auth_params = {"client_id": "test_client", "response_type": "urn:ietf:params:oauth:grant-type:device_code",
                       "redirect_uri": "https://www.google.com/"}
        self.response = self.client.request("GET", "/authorize/", params=self.auth_params,
                                            name="6/authorize/ device_code flow")
        # assert self.response.status_code == status.HTTP_200_OK

    @task
    def test_user_authorization(self):
        # Stage 4: User authorizes the client
        # In a real scenario, this would be done manually by the user in a web browser.
        # This is just a test, so we're simulating this step by making a request with the user's credentials.
        self.auth_params = {
            "client_id": "test_client",
            "response_type": "urn:ietf:params:oauth:grant-type:device_code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
            "username": "TestClient",
            "password": "test_password",
        }
        self.response = self.client.request("POST", "/authorize/",
                                        data=self.auth_params,
                                        headers={"Content-Type": self.content_type},
                                        cookies={"user_code": self.user_code},
                                        name="7/authorize/ device_code flow")
        # logging.info(f"test_user_authorization; self.response.status_code: {self.response.status_code}")
        # assert self.response.status_code == status.HTTP_302_FOUND

    @task
    def test_obtain_access_token(self):
        # Stage 5: Client exchanges the device code for an access token
        self.token_params = {"client_id": "test_client", "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "device_code": self.device_code, "redirect_uri": "https://www.google.com/"}
        self.response = self.client.request("POST", "/token/", data=self.token_params,
                                        headers={"Content-Type": self.content_type},
                                            name="8/token/  device_code flow")
        # assert self.response.status_code == status.HTTP_200_OK

        # Verify that the client received an access token
        self.access_token = self.response.json().get("access_token")
        # logging.info(f"test_obtain_access_token; self.access_token: {self.access_token}")
        # assert self.access_token is not None

class TaskSetDevicePostCancel(SequentialTaskSet):
    content_type = "application/x-www-form-urlencoded"
    @task
    def test_device_POST(self) -> None:
        # Stage 1: Client requests a device code
        self.request_params = {"client_id": "test_client",
                          "scope": "openid"}
        self.response = self.client.request("POST", "/device/", data=self.request_params,
                                        headers={"Content-Type": self.content_type},
                                            name="1/device/")
        self.response_data = self.response.json()
        self.device_code = self.response_data.get("device_code")
        self.user_code = self.response_data.get("user_code")

    @task
    def test_successful_device_cancel(self) -> None:

        self.param_next = {
            "client_id": "test_client",
            "scope": f"user_code={self.user_code}",
        }
        self.response = self.client.request(
            "DELETE", "/device/auth/cancel", data=self.param_next,
            headers={'Content-Type': self.content_type, "Cookie": self.param_next["scope"]},
            name="9/device/auth/cancel"
        )
        # logging.info(f"test_successful_device_cancel; user_code: {self.user_code}")
        # logging.info(f"test_successful_device_cancel; response.status_code: {self.response.status_code}")
        # assert self.response.status_code == status.HTTP_200_OK

