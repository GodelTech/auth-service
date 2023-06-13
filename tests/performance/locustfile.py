from locust import HttpUser, between
from tests.performance import (
    TaskSetClientEndpoint,
    TaskSetDeviceFlow,
    TaskSetDevicePostCancel,
    TaskSetAuthorizationCodeFlow,
    TaskSetInfoEndpoint,
    TaskSetUserEndpoint,
    # TaskSetRevokationEndpoint,
    TaskSetEndsessionEndpoint,
    TaskSetIntrospectionEndpoint,
    TaskSetThirdPartyProviders
)

class LoadTestEndpoint(HttpUser):
    wait_time = between(1, 5)
    tasks = [
        # TaskSetClientEndpoint,      # +++; 5_tasks
        # TaskSetDeviceFlow,      # +++; 8-tasks;
        # TaskSetDevicePostCancel,    # +++; 2_tasks;
        # TaskSetAuthorizationCodeFlow,    # +++; 3_tasks;
        # TaskSetInfoEndpoint,          # +++; 3_tasks;
        # TaskSetUserEndpoint,         #  +++; 4_tasks;
        # TaskSetEndsessionEndpoint    # +++; 1_task
        # TaskSetIntrospectionEndpoint   # +++; 1_task
        TaskSetThirdPartyProviders
    ]


