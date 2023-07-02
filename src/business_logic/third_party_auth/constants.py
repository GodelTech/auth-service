from enum import Enum


class AuthProviderName(Enum):
    """
    Enumeration of supported authentication provider names.

    This enumeration defines the names of supported authentication providers.
    Each provider name is associated with a specific string value.

    Attributes:
        GITHUB (str): GitHub authentication provider.
        GITLAB (str): GitLab authentication provider.
        GOOGLE (str): Google authentication provider.
        MICROSOFT (str): Microsoft authentication provider.
        LINKEDIN (str): LinkedIn authentication provider.

    """

    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"


class StateData(Enum):
    """
    Enumeration of state data values for third-party authentication.

    This enumeration defines the values associated with various state data parameters used in third-party authentication flows.
    Each value represents a specific data parameter.

    Attributes:
        REDIRECT_URL (int): Value representing the redirect URL in state data.
        CODE (int): Value representing the code in state data.
        CLIENT_ID (int): Value representing the client ID in state data.
        STATE_LENGTH (int): Value representing the expected length of the state data.

    """

    REDIRECT_URL = -1
    CODE = 0
    CLIENT_ID = 1
    STATE_LENGTH = 3
