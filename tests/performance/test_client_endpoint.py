import json
import logging
from locust import TaskSet, SequentialTaskSet, task


class TaskSetClientEndpoint(SequentialTaskSet):
    content_type = "application/x-www-form-urlencoded"

    def on_start(self):
        self.request_body_post = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }
        self.wrong_request_body_post = {
            "redirect_uris": [],
            "client_name": "Test Client Registration",
            "client_uri": "https://example.com",
            "logo_uri": "https://example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }
        self.request_body_put = {
            "client_name": "Test Client Registration",
        }
        self.client_id_put = "non_existent_client"
        self.wrong_request_body_put = {
            "redirect_uris": ["https://example.com/callback"],
            "client_name": "Updated Client",
            "client_uri": "https://updated-example.com",
            "logo_uri": "https://updated-example.com/logo.png",
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
            "scope": "openid email"
        }
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

    @task
    def test_successful_registration_request(self) -> None:
        self.response = self.client.request(
            "POST",
            "/clients/register",
            data=self.request_body_post,
            headers={"Content-Type": self.content_type},
            name="1/clients/register"
        )
        try:
            self.client_id = self.response.json()["client_id"]
        except Exception as e:
            raise e

    @task
    def test_successful_client_get(self) -> None:
        self.client.request("GET", "/clients/test_client", name="2/clients/test_client")


    @task
    def test_successful_client_update(self) -> None:
        self.client.request("PUT", "/clients/test_client",
                            data=self.request_body_put,
                            name="3/clients/test_client")

    @task
    def test_successful_client_deletion(self) -> None:
        self.client.request("DELETE", f"/clients/{self.client_id}",
                            name="4/clients/{self.client_id}")

    @task
    def test_successful_get_all_clients(self) -> None:
        self.client.get(
            "/clients",
            headers={
                "access-token": self.access_token,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            name="5/clients")


