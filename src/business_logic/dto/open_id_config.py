from typing import Optional

from pydantic import BaseModel


class OpenIdConfiguration(BaseModel):
    issuer: str
    jwks_uri: str
    authorization_endpoint: str
    token_endpoint: str
    id_token_signing_alg_values_supported: list[str]
    subject_types_supported: list[str]
    response_types_supported: list[str]

    claims_supported: Optional[list[str]]
    scopes_supported: Optional[list[str]]
    registration_endpoint: Optional[str]
    userinfo_endpoint: Optional[str]
    end_session_endpoint: Optional[str]
    check_session_iframe: Optional[str]

    grant_types_supported: Optional[list[str]]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:  # pragma: no cover
        return f"Model {self.__class__.__name__}"
