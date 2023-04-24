from .github import GithubAuthService
from .gitlab import GitlabAuthService
from .google import GoogleAuthService
from .linkedin import LinkedinAuthService
from .microsoft import MicrosoftAuthService


__all__ = [
    "GithubAuthService",
    "GitlabAuthService",
    "GoogleAuthService",
    "LinkedinAuthService",
    "MicrosoftAuthService",
]
