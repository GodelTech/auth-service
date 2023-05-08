from enum import Enum


class ResponseType(Enum):
    CODE = "code"
    DEVICE = "urn:ietf:params:oauth:grant-type:device_code"
    TOKEN = "token"
    ID_TOKEN = "id_token"
    ID_TOKEN_TOKEN = "id_token token"
