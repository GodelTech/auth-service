from enum import Enum


class AuthProviderName(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
