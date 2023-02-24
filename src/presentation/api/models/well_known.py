from typing import Optional, Any
import logging
from pydantic import BaseModel

class ResponseOpenIdConfiguration(BaseModel):
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
    frontchannel_logout_session_supported: Optional[bool]
    frontchannel_logout_supported: Optional[bool]
    end_session_endpoint: Optional[str]
    check_session_iframe: Optional[str]
    op_tos_uri: Optional[str]
    op_policy_uri: Optional[str]
    require_request_uri_registration: Optional[bool]
    request_uri_parameter_supported: Optional[bool]
    request_parameter_supported: Optional[bool]
    claims_parameter_supported: Optional[bool]
    ui_locales_supported: Optional[list[str]]
    claims_locales_supported: Optional[list[str]]
    service_documentation: Optional[list[str]]
    claim_types_supported: Optional[list[str]]
    display_values_supported: Optional[list[str]]
    token_endpoint_auth_signing_alg_values_supported: Optional[list[str]]
    token_endpoint_auth_methods_supported: Optional[list[str]]
    request_object_encryption_enc_values_supported: Optional[list[str]]
    request_object_encryption_alg_values_supported: Optional[list[str]]
    request_object_signing_alg_values_supported: Optional[list[str]]
    userinfo_encryption_enc_values_supported: Optional[list[str]]
    userinfo_encryption_alg_values_supported: Optional[list[str]]
    userinfo_signing_alg_values_supported: Optional[list[str]]
    id_token_encryption_enc_values_supported: Optional[list[str]]
    id_token_encryption_alg_values_supported: Optional[list[str]]
    acr_values_supported: Optional[list[str]]
    grant_types_supported: Optional[list[str]]
    response_modes_supported: Optional[list[str]]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"

class ResponseJWKS(BaseModel):
    keys: list[Any]

    # kty: str # RS256
    # kid : Optional[str]  # key id in case we have more than one keyy
    # use : str  # "sig" or "enc"
    # n : str  # module
    # e : str  # graduation

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"
