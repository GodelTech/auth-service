from tests.performance.test_client_endpoint import (
    # TaskSetClientEndpointGET,
    # TaskSetClientEndpointPUT,
    TaskSetClientEndpoint,
    # TaskSetClientAllEndpointGET
)
from tests.performance.test_device_flow import (
    TaskSetDeviceFlow,
    TaskSetDevicePostCancel
)
from tests.performance.test_authorization_code_flow import TaskSetAuthorizationCodeFlow
from tests.performance.test_userinfo_endpoint import TaskSetInfoEndpoint
from tests.performance.test_user import TaskSetUserEndpoint
from tests.performance.test_endsession_endpoint import TaskSetEndsessionEndpoint
# from tests.performance.test_revoke_endpoint import TaskSetRevokationEndpoint
from tests.performance.test_introspection_endpoint import TaskSetIntrospectionEndpoint
from tests.performance.test_third_party_providers import TaskSetThirdPartyProviders