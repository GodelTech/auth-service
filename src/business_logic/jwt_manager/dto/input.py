from pydantic import BaseModel
from typing import Optional


class BaseJWTPayload(BaseModel):
    sub: str
    iss: str
    iat: int
    exp: int
    aud: str
    client_id: str
    jti: str
    acr: Optional[int]


class AccessTokenPayload(BaseJWTPayload):
    typ: str = 'Bearer'


class RefreshTokenPayload:
    ...


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
