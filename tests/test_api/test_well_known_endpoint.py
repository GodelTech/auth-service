import json
import jwt
import pytest
from fastapi import status
from httpx import AsyncClient
from src.business_logic.services.jwt_token import JWTService
from jwkest import base64_to_long
from Crypto.PublicKey.RSA import construct


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestWellKnown:
    async def test_successful_openid_config_request(
        self, client: AsyncClient
    ) -> None:
        KEYS_REQUIRED = (
            "issuer",
            "jwks_uri",
            "authorization_endpoint",
            "token_endpoint",
            "id_token_signing_alg_values_supported",
            "subject_types_supported",
            "response_types_supported",
        )

        KEYS_OPTIONAL = (
            "claims_supported",
            "scopes_supported",
            "registration_endpoint",
            "userinfo_endpoint",
            "frontchannel_logout_session_supported",
            "frontchannel_logout_supported",
            "end_session_endpoint",
            "check_session_iframe",
            "op_tos_uri",
            "op_policy_uri",
            "require_request_uri_registration",
            "request_uri_parameter_supported",
            "request_parameter_supported",
            "claims_parameter_supported",
            "ui_locales_supported",
            "claims_locales_supported",
            "service_documentation",
            "claim_types_supported",
            "display_values_supported",
            "token_endpoint_auth_signing_alg_values_supported",
            "token_endpoint_auth_methods_supported",
            "request_object_encryption_enc_values_supported",
            "request_object_encryption_alg_values_supported",
            "request_object_signing_alg_values_supported",
            "userinfo_encryption_enc_values_supported",
            "userinfo_encryption_alg_values_supported",
            "userinfo_signing_alg_values_supported",
            "id_token_encryption_enc_values_supported",
            "id_token_encryption_alg_values_supported",
            "acr_values_supported",
            "grant_types_supported",
            "response_modes_supported",
        )

        response = await client.request(
            "GET", "/.well-known/openid-configuration"
        )
        assert response.status_code == status.HTTP_200_OK

        response_content = json.loads(response.content.decode("utf-8"))
        for key in KEYS_REQUIRED:
            assert key in response_content.keys()
            response_content.pop(key, None)

        for key in response_content.keys():
            assert key in KEYS_OPTIONAL

    async def test_successful_jwks_request(self, client: AsyncClient) -> None:
        response = await client.request(method="GET", url="/.well-known/jwks")
        response_content = json.loads(response.content.decode("utf-8"))
        assert response.status_code == status.HTTP_200_OK
        assert type(response_content["keys"]) == list
        assert type(response_content["keys"][0]) == dict

        jwt_service = JWTService()
        response_content = response_content["keys"][0]
        test_token = await jwt_service.encode_jwt(payload={"sub": 1})

        if response_content["alg"] == "RS256":
            n = base64_to_long(response_content["n"])
            e = base64_to_long(response_content["e"])

            test_key = construct((n, e))

            assert (
                jwt_service.keys.public_key
                == test_key.public_key().export_key("PEM")
            )
            assert response_content["kty"] == "RSA"
            assert bool(
                await jwt_service.decode_token(
                    token=test_token,
                    # key=test_key.public_key().export_key('PEM'),
                    # algorithms=["RS256",]
                )
            )
            assert response_content["use"] == "sig"
