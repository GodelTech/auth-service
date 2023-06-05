from locust import HttpUser, task, between
from tests.performance import (
    TaskSetClientEndpoint,
    TaskSetDeviceFlow,
    TaskSetDevicePostCancel,
    TaskSetAuthorizationCodeFlow
)

class TestClientEndpointPOSTthenDELETE(HttpUser):
    wait_time = between(1, 5)
    tasks = [
        # TaskSetAuthorizeEndpointGET,      # +
        # TaskSetAuthorizeEndpointPOST,      # +
        # TaskSetClientEndpoint,      # +++; 5_tasks
        # TaskSetDeviceFlow,      # +++; 8-tasks; -(assert self.response.status_code == status.HTTP_302_FOUND)
        # TaskSetDevicePostCancel,    # +++; 2_tasks;
        TaskSetAuthorizationCodeFlow    # +; 3_tasks;
    ]


