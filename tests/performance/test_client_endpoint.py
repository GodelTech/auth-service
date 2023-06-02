# import uuid
#
# import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import select, insert
# from sqlalchemy.orm import sessionmaker
from importlib import import_module
import logging
from locust import TaskSet, HttpUser, SequentialTaskSet, task, between

# from src.business_logic.services import JWTService                 # !!! circular import
# from src.data_access.postgresql.repositories import ClientRepository
from src.data_access.postgresql.tables.client import Client
from tests.conftest import connection


class TaskSetClientEndpointPOSTthenDELETE(SequentialTaskSet):
    content_type = "application/x-www-form-urlencoded"

    def on_start(self):
        self.request_body = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }
        self.wrong_request_body = {
            "redirect_uris": [],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }

    @task
    def test_successful_registration_request(self) -> None:
        self.response = self.client.request(
            "POST",
            "/clients/register",
            data=self.request_body,
            headers={"Content-Type": self.content_type},
            name="/clients/register"
        )
        try:
            self.client_id = self.response.json()["client_id"]
        except Exception as e:
            raise e

    @task
    def test_successful_client_deletion(self) -> None:
        self.client.request("DELETE", f"/clients/{self.client_id}",
                            name="/clients/{self.client_id}")

    @task
    def test_unsuccessful_registration_request(self) -> None:
        self.response = self.client.request("POST",
                                            "/clients/register",
                                            data=self.wrong_request_body,
                                            headers={"Content-Type": self.content_type},
                                            name="/clients/register")

class TaskSetClientEndpointPUT(TaskSet):
    content_type = "application/x-www-form-urlencoded"

    def on_start(self):
        self.request_body = {
            "client_name": "Test Client Registration",
        }
        self.client_id = "non_existent_client"
        self.wrong_request_body = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Updated Client",
            "client_uri": "https://updated-example.com",
            "logo_uri": "https://updated-example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }

    @task(5)
    def test_successful_client_update(self) -> None:
        self.client.request("PUT", "/clients/test_client",
                            data=self.request_body,
                            name="/clients/test_client")

    @task
    def test_unsuccessful_update(self) -> None:
        self.client.request("PUT", f"/clients/{self.client_id}",
                            data=self.wrong_request_body,
                            name="/clients/test_client")

######################## ERROR ###########################################
class TaskSetClientAllEndpointGET(TaskSet):

    def on_start(self):
        # Stage 1: Authorization endpoint creates a record with a secret code in the Persistent Grant table
        authorization_params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": "https://www.google.com/",
        }
        self.authorization_response = self.client.request("GET", "/authorize/", params=authorization_params)
        assert self.authorization_response.status_code == status.HTTP_200_OK

        user_credentials = {"username": "PeterParker", "password": "the_beginner"}
        self.response = self.client.request(
            "POST",
            "/authorize/",
            data={**authorization_params, **user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        logging.info(f"Actual status code: {self.response.status_code}")
        logging.info(f"Full response: {self.response.text}")          # get status.HTTP_200
        # assert self.response.status_code == status.HTTP_302_FOUND

        # Stage 2: Token endpoint changes the secret code in the Persistent Grant table to a token
        logging.info(f"!!!!!self.response: {self.response}!!!!!!")
        logging.info(f"!!!!!self.response.headers: {self.response.headers}!!!!!!")
        self.secret_code = self.response.headers["location"].split("=")[1]

        token_params = {
            "client_id": "spider_man",
            "grant_type": "authorization_code",
            "code": self.secret_code,
            "redirect_uri": "https://www.google.com/",
        }
        self.token_response = self.client.request(
            "POST",
            "/token/",
            data=token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.response_data = self.token_response.json()
        self.access_token = self.response_data.get("access_token")

    @task(5)
    def test_successful_get_all_clients(self) -> None:
        self.client.request("GET", "/clients",
                            headers={
                            "access-token": self.access_token,
                            "Content-Type": "application/x-www-form-urlencoded",
                            },
                            name="/clients")

    @task
    def test_unsuccessful_get_all_clients(self) -> None:
        self.client.request("GET", "/clients", name="/clients")


class TaskSetClientEndpointGET(TaskSet):
    @task(5)
    def test_successful_client_get(self) -> None:
        self.client.request("GET", "/clients/test_client", name="/clients/test_client")

    @task
    def test_unsuccessful_client_get(self) -> None:
        self.client.request("GET", "/clients/invalid_test_client", name="/clients/test_client")



