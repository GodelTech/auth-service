from typing import Optional

from pydantic import BaseModel


class ResponseOpenIdConfiguration(BaseModel):
    issuer: str
    jwks_uri: str
    authorization_endpoint: str
    token_endpoint: str
    id_token_signing_alg_values_supported: list
    subject_types_supported: list
    response_types_supported: list

    claims_supported: Optional[list]
    scopes_supported: Optional[list]
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
    ui_locales_supported: Optional[list]
    claims_locales_supported: Optional[list]
    service_documentation: Optional[list]
    claim_types_supported: Optional[list]
    display_values_supported: Optional[list]
    token_endpoint_auth_signing_alg_values_supported: Optional[list]
    token_endpoint_auth_methods_supported: Optional[list]
    request_object_encryption_enc_values_supported: Optional[list]
    request_object_encryption_alg_values_supported: Optional[list]
    request_object_signing_alg_values_supported: Optional[list]
    userinfo_encryption_enc_values_supported: Optional[list]
    userinfo_encryption_alg_values_supported: Optional[list]
    userinfo_signing_alg_values_supported: Optional[list]
    id_token_encryption_enc_values_supported: Optional[list]
    id_token_encryption_alg_values_supported: Optional[list]
    acr_values_supported: Optional[list]
    grant_types_supported: Optional[list]
    response_modes_supported: Optional[list]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"
