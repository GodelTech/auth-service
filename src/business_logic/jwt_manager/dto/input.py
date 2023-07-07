from pydantic import BaseModel
from typing import Optional, Any, Union
from src.dyna_config import DOMAIN_NAME
import uuid

class BaseJWTPayload(BaseModel):
    sub: Union[int, str]  # user id
    iat: int  # time of creation
    exp: int  # time when token will expire
    aud: Optional[Union[str, list[str]]]  # name for whom token was generated
    client_id: str  # id of the client who issued a token
    acr: Optional[int]  # default 0
    jti: str = str(uuid.uuid4()) # uniques identifier for token, UUID4
    iss: str = DOMAIN_NAME  # auth service uri


class AccessTokenPayload(BaseJWTPayload):
    typ: str = 'Bearer'


class RefreshTokenPayload(BaseModel):
    jti: str


class IdTokenPayload(BaseJWTPayload):
    typ: str = 'ID'
    email: Optional[str] = None
    email_verified: Optional[str] = None
    given_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_username: Optional[str] = None
    picture: Optional[str] = None
    zoneinfo: Optional[str] = None
    locale: Optional[str] = None

class AdminUIPayload(BaseModel):
    sub:int
    exp:int
    aud:list[str] = ["oidc:admin_ui"]