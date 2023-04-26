from enum import Enum


class AuthProviderName(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"


class StateData(Enum):
    REDIRECT_URL = -1
    CODE = 0
    CLIENT_ID = 1
    STATE_LENGTH = 3
