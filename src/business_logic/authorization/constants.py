from enum import Enum


class ResponseType(Enum):
    """
    Enumerates the response types used in OAuth 2.0.

    Each response type represents a specific grant type or token type that can be requested in the OAuth flow.

    The available response types are:
        - CODE: Authorization code grant type.
        - DEVICE: Device code grant type.
        - TOKEN: Implicit grant type, returns only an access token.
        - ID_TOKEN: Implicit grant type, returns only an ID token.
        - ID_TOKEN_TOKEN: Implicit grant type, returns both an ID token and an access token.

    Reference:
        - https://www.rfc-editor.org/rfc/rfc6749#section-3.1.1
        - https://openid.net/specs/openid-connect-core-1_0.html#Authentication
    """

    CODE = "code"
    DEVICE = "urn:ietf:params:oauth:grant-type:device_code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    ID_TOKEN_TOKEN = "id_token token"
