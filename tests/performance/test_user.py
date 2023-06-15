import logging
import uuid
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
        )

    @task
    def test_successful_register_post(self) -> None:
        self.headers_a = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.unique_username = str(uuid.uuid4())
        self.data_a = {
            "username": self.unique_username,
            "email": f"{self.unique_username}@mail",
            "password": f"{self.unique_username}password",
        }
        self.client.request(
            "POST", "/user/register", headers=self.headers_a, data=self.data_a,
        )


    @task
    def test_successful_add_info_get(self) -> None:
        self.client.request(
            "GET", f"/user/add_info/{self.unique_username}?scope=profile",
            headers=self.headers,
            data=self.data_first,
            name="/user/add_info/unique_username?scope=profile"
        )

    @task
    def test_successful_add_info_post(self) -> None:
        self.client.request(
            "POST", f"/user/add_info/{self.unique_username}",
            headers=self.headers,
            data=self.data_second,
            name="/user/add_info/unique_username"
        )
