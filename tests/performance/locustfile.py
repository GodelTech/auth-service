from locust import HttpUser, task, between
from tests.performance import (
    TaskSetClientEndpoint,
    TaskSetDeviceFlow,
    TaskSetDevicePostCancel,
    TaskSetAuthorizationCodeFlow,
    TaskSetInfoEndpoint,
    # TaskSetUserEndpoint,
    # TaskSetRevokationEndpoint
)

class LoadTestEndpoint(HttpUser):
    wait_time = between(1, 5)
    tasks = [
        # TaskSetClientEndpoint,      # +++; 5_tasks
        # TaskSetDeviceFlow,      # +++; 8-tasks; -(assert self.response.status_code == status.HTTP_302_FOUND)
        # TaskSetDevicePostCancel,    # +++; 2_tasks;
        TaskSetAuthorizationCodeFlow,    # +; 3_tasks;
        # TaskSetInfoEndpoint,          # -
        # TaskSetUserEndpoint,         #  -
    ]


