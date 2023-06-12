from pydantic import BaseModel
from typing import Optional, Any, Union


class BaseJWTPayload(BaseModel):
    sub: Union[int, str]  # user id
    iss: str  # auth service uri
    iat: int  # time of creation
    exp: int  # time when token will expire
    aud: Optional[Union[str, list[str]]]  # name for whom token was generated
    client_id: str  # id of the client who issued a token
    jti: str  # uniques identifier for token, UUID4
    acr: Optional[int]  # default 0


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
