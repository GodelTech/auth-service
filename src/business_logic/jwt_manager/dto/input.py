from pydantic import BaseModel
from typing import Optional


class BaseJWTPayload(BaseModel):
    sub: Optional[str]
    iss: Optional[str]
    client_id: Optional[str]
    iat: Optional[int]
    exp: Optional[int]
    claims: Optional[list[str]]
    scope: Optional[str]
    aud: Optional[str]
