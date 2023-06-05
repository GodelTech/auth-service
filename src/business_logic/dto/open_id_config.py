from pydantic import BaseModel


class OpenIdConfiguration(BaseModel):
    issuer: str
    jwks_uri: str
    authorization_endpoint: str
    token_endpoint: str
    id_token_signing_alg_values_supported: list
    subject_types_supported: list
    response_types_supported: list
    claims_supported: list
    scopes_supported: list
    registration_endpoint: str
    userinfo_endpoint: str
    frontchannel_logout_session_supported: bool
    end_session_endpoint: str
    check_session_iframe: str
    grant_types_supported: list
