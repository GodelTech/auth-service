from pydantic import BaseModel
from typing import Optional, Any


class BaseJWTPayload(BaseModel):
    sub: str  # user id
    iss: str  # auth service uri
    iat: int  # time of creation
    exp: int  # time when token will expire
    aud: str  # name for whom token was generated
    client_id: str  # id of the client who issued a token
    jti: str  # uniques identifier for token, UUID4
    acr: Optional[int]  # default 0


class AccessTokenPayload(BaseJWTPayload):
    typ: str = 'Bearer'


class RefreshTokenPayload(BaseModel):
    jti: str


class IdTokenPayload(BaseJWTPayload):
    typ: str = 'ID'
    email: Optional[str]
    email_verified: Optional[str]
    given_name: Optional[str]
    last_name: Optional[str]
    preferred_username: Optional[str]
    picture: Optional[str]
    zoneinfo: Optional[str]
    locale: Optional[str]
