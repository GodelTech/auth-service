import logging
import uuid
from urllib import parse

from locust import TaskSet, SequentialTaskSet, task


class TaskSetEndsessionEndpoint(SequentialTaskSet):

    @task
    def get_access_and_id_tokens(self):
        # Creating new uniq user
        self.unique_username = str(uuid.uuid4())
        self.data_new_user = {
            "username": self.unique_username,
            "email": f"{self.unique_username}@mail",
            "password": f"{self.unique_username}password",
        }
        self.client.request(
            "POST", "/user/register",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=self.data_new_user,
            name="/user/register"
        )

        # authorizing new user
        self.authorization_params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": "https://www.google.com/",
        }
        self.user_credentials = {"username": self.unique_username,
                                 "password": f"{self.unique_username}password"}

        self.response_post = self.client.request(
            "POST",
            "/authorize/",
            data={**self.authorization_params, **self.user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Obtaining tokens. For endsession id_token is required
        self.secret_code = self._get_code(url=self.response_post.url)
        self.token_params = {
            "client_id": "test_client",
            "grant_type": "authorization_code",
            "code": self.secret_code,
            "redirect_uri": "https://www.google.com/",
        }
        self.token_response = self.client.request(
            "POST",
            "/token/",
            data=self.token_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.response_data = self.token_response.json()
        self.access_token = self.response_data.get("access_token")
        self.id_token = self.response_data.get("id_token")

    @task
    def test_revoke(self):
        headers = {
            "authorization": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"token": self.access_token, "token_type_hint": "access_token"}
        self.client.request(
            method="POST", url="/revoke/", data=params, headers=headers
        )

    @task
    def test_end_session(self):
        self.logout_params = {
            "id_token_hint": self.id_token,
        }
        self.end_session_response = self.client.request("GET", "/endsession/",
                                                        params=self.logout_params,
                                                        name="/endsession/")

    def _get_code(self, url):
        self.parsed_url = parse.urlparse(url)
        self.query_parameters = parse.parse_qs(self.parsed_url.query)
        self.continue_url = self.query_parameters.get("continue", [None])[0]
        if self.continue_url is not None:
            self.continue_url_decoded = parse.unquote(self.continue_url)
            self.code_url = parse.urlparse(self.continue_url_decoded)
            self.code_parameters = parse.parse_qs(self.code_url.query)
            self.secret_code = self.code_parameters.get("code", [None])[0]
            return self.secret_code
        else:
            self.secret_code = self.response_post.url.split("=")[1]
            return self.secret_code