from locust import HttpUser, task, between
from tests.performance import (
    TaskSetAuthorizeEndpointGET,
    TaskSetAuthorizeEndpointPOST,
    TaskSetClientEndpointPOSTthenDELETE,
    TaskSetClientEndpointPUT,
    TaskSetClientEndpointGET,
    TaskSetClientAllEndpointGET,
    TaskSetDeviceEndpoint
)

class TestClientEndpointPOSTthenDELETE(HttpUser):
    wait_time = between(1, 5)
    tasks = [
        # TaskSetAuthorizeEndpointGET,
        # TaskSetAuthorizeEndpointPOST,
        # TaskSetClientEndpointPOSTthenDELETE,
        # TaskSetClientEndpointPUT,
        # TaskSetClientEndpointGET,
        # TaskSetClientAllEndpointGET,
        TaskSetDeviceEndpoint
    ]


