import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import Request
from jwkest import base64_to_long, long_to_base64

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.tables.users import UserClaim

logger = logging.getLogger(__name__)


class WellKnownServies:
    def __init__(self) -> None:
        self._request: Optional[Request] = None

    def get_list_of_types(
        self, list_of_types: List[Tuple[str, str]] = [("Not ready yet", "")]
    ) -> List[str]:
        return [claim[0] for claim in list_of_types]

    def get_all_urls(self, result: Dict[str, str]) -> Optional[Dict[str, str]]:
        if self.request is not None:
            return {
                route.name: result["issuer"] + route.path
                for route in self.request.app.routes
            } | {"false": "/ Not ready yet"}
        return None

    async def get_openid_configuration(
        self,
    ) -> Optional[Dict[str, Any]]:
        # For key description: https://ldapwiki.com/wiki/Openid-configuration
        # REQUIRED
        if self.request is not None:
            result: Dict[str, Any] = {
                "issuer": str(self.request.url).replace(
                    "/.well-known/openid-configuration", ""
                )
            }

            urls_dict = self.get_all_urls(result)
            if urls_dict is not None:
                result["jwks_uri"] = urls_dict["false"]
                result["authorization_endpoint"] = urls_dict["get_authorize"]
                result[
                    "id_token_signing_alg_values_supported"
                ] = self.get_list_of_types()
                result["subject_types_supported"] = self.get_list_of_types()
                result["response_types_supported"] = self.get_list_of_types()

                # may be REQUIRED
                result["token_endpoint"] = urls_dict["get_tokens"]
                result["end_session_endpoint"] = urls_dict["false"]
                result["check_session_iframe"] = urls_dict["false"]

                # RECOMMENDED
                result["claims_supported"] = self.get_list_of_types(
                    UserClaim.USER_CLAIM_TYPE
                )
                result["scopes_supported"] = self.get_list_of_types()
                result["registration_endpoint"] = urls_dict["false"]
                result["userinfo_endpoint"] = urls_dict["get_userinfo"]

                # OPTIONAL
                result[
                    "frontchannel_logout_session_supported"
                ] = False  # i don't know
                result["frontchannel_logout_supported"] = False  # i don't know
                result["op_tos_uri"] = urls_dict["false"]
                result["op_policy_uri"] = urls_dict["false"]
                result[
                    "require_request_uri_registration"
                ] = False  # i don't know
                result[
                    "request_uri_parameter_supported"
                ] = False  # i don't know
                result["request_parameter_supported"] = False  # i don't know
                result["claims_parameter_supported"] = False  # i don't know
                result["ui_locales_supported"] = self.get_list_of_types()
                result["claims_locales_supported"] = self.get_list_of_types()
                result["service_documentation"] = self.get_list_of_types()
                result["claim_types_supported"] = self.get_list_of_types()
                result["display_values_supported"] = self.get_list_of_types()
                result[
                    "token_endpoint_auth_signing_alg_values_supported"
                ] = self.get_list_of_types()
                result[
                    "token_endpoint_auth_methods_supported"
                ] = self.get_list_of_types()
                result[
                    "request_object_encryption_enc_values_supported"
                ] = self.get_list_of_types()
                result[
                    "request_object_encryption_alg_values_supported"
                ] = self.get_list_of_types()
                result[
                    "request_object_signing_alg_values_supported"
                ] = self.get_list_of_types()
                result[
                    "userinfo_encryption_enc_values_supported"
                ] = self.get_list_of_types()
                result[
                    "userinfo_encryption_alg_values_supported"
                ] = self.get_list_of_types()
                result[
                    "userinfo_signing_alg_values_supported"
                ] = self.get_list_of_types()
                result[
                    "id_token_encryption_enc_values_supported"
                ] = self.get_list_of_types()
                result[
                    "id_token_encryption_alg_values_supported"
                ] = self.get_list_of_types()
                result["acr_values_supported"] = self.get_list_of_types()
                result["grant_types_supported"] = self.get_list_of_types(
                    PersistentGrant.TYPES_OF_GRANTS
                )
                result["response_modes_supported"] = self.get_list_of_types()
                # result[""] = urls_dict['false']

                return result
        return None

    async def get_jwks(self) -> Dict[str, Any]:
        jwt_service = JWTService()
        kty = ""
        if "RS" in jwt_service.algorithm:
            kty = "RSA"
        elif "HS" in jwt_service.algorithm:
            kty = "HMAC"
        else:
            raise ValueError

        result = {
            "kty": kty,
            "alg": jwt_service.algorithm,
            "use": "sig",
            # "kid" : ... ,
            "n": long_to_base64(await jwt_service.get_module()),
            "e": long_to_base64(await jwt_service.get_pub_key_expanent()),
        }
        logger.info(
            f"n =  {base64_to_long(result['n'])}\ne = {base64_to_long(result['e'])}"
        )
        return result

    @property
    def request(self) -> Request:
        return self._request

    @request.setter
    def request(self, request_model: Request) -> None:
        self._request = request_model
