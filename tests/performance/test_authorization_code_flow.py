import logging
from urllib import parse
from locust import TaskSet, SequentialTaskSet, task


class TaskSetAuthorizationCodeFlow(SequentialTaskSet):

    def on_start(self):
        self.authorization_params = {
            "client_id": "spider_man",
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": "https://www.google.com/",
        }
        self.user_credentials = {"username": "TestClient", "password": "test_password"}

    @task
    def test_successful_authorization_GET(self) -> None:
        # Stage 1: Authorization endpoint creates a record with a secret code in the Persistent Grant table
        self.authorization_response = self.client.request("GET", "/authorize/",
                                                          params=self.authorization_params,
                                                          name="/authorize/")

    @task
    def test_successful_authorization_POST(self):
        self.response_post = self.client.request(
            "POST",
            "/authorize/",
            data={**self.authorization_params, **self.user_credentials},
            headers={"Content-Type": "application/x-www-form-urlencoded"})

    @task
    def test_obtain_access_token(self):
        self.secret_code = self._get_code(url=self.response_post.url)
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
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        self.response_data = self.token_response.json()
        self.access_token = self.response_data.get("access_token")
        self.id_token = self.response_data.get("id_token")

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