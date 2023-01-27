from typing import Any, Dict, List, Optional, Tuple

import httpx

from errors import GetIdEmailError
from oauth2 import BaseOAuth2, OAuth2Error


BASE_SCOPES = ["openid", "email"]


class OpenIDConfigurationError(OAuth2Error):
    pass


class IdentityOAuth2(BaseOAuth2[Dict[str, Any]]):
    pass