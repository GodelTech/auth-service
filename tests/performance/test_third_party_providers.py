import uuid
from locust import TaskSet, SequentialTaskSet, task

class TaskSetThirdPartyProviders(SequentialTaskSet):

    @task
    def test_post(self):
        self.unique_code = str(uuid.uuid4())
        self.STUB_STATE = f"{self.unique_code}!_!spider_man!_!https://www.google.com/"
        self.post_params = {
            "state": self.STUB_STATE
        }
        self.client.request(
            "POST", "/authorize/oidc/state",
            data=self.post_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="/authorize/oidc/state"
        )
