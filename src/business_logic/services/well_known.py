from src.data_access.postgresql.tables.persistent_grant import TYPES_OF_GRANTS
from src.business_logic.services.jwt_token import JWTService
from jwkest import long_to_base64, base64_to_long
import logging
from src.dyna_config import BASE_URL
from jwkest import base64_to_long, long_to_base64
from fastapi import Request
from src.business_logic.services.jwt_token import JWTService
from typing import Any, Union
from src.data_access.postgresql.repositories import WellKnownRepository

logger = logging.getLogger(__name__)


class WellKnownServices:
    def __init__(self, wlk_repo: WellKnownRepository) -> None:
        self.request: Union[Request, Any] = None
        self.wlk_repo = wlk_repo

    def get_list_of_types(
        self, list_of_types: list[Any] = [("Not ready yet", "")]
    ) -> list[str]:
        return [claim[0] for claim in list_of_types]

    def get_all_urls(self, result: dict[str, Any]) -> dict[str, Any]:
        if self.request is None:
            raise ValueError
        return {
            route.name: result["issuer"] + route.path
            for route in self.request.app.routes
        } | {"false": "/ Not ready yet"}

    def get_algorithms(self):
        return JWTService().algorithms

    async def get_claims(self):
        result = await self.wlk_repo.get_user_claim_types()
        # result += await self.wlk_repo.get_client_claim_types()
        return result

    async def get_grant_types(self):
        result = await self.wlk_repo.get_grant_types()
        # result += await self.wlk_repo.get_client_claim_types()
        return result

    async def get_openid_configuration(
        self,
    ) -> dict[str, Any]:
        if self.request is None:
            raise ValueError

        # For key description: https://ldapwiki.com/wiki/Openid-configuration

        # REQUIRED
        result: dict[str, Any] = {}
        result["issuer"] = f"http://{BASE_URL}"

        urls_dict = self.get_all_urls(result)

        result["jwks_uri"] = urls_dict["get_jwks"]
        result["authorization_endpoint"] = urls_dict["get_authorize"]
        result["id_token_signing_alg_values_supported"] = self.get_algorithms()
        result["subject_types_supported"] = [
            "public"
        ]  # https://openid.net/specs/openid-connect-core-1_0.html#SubjectIDTypes
        result["response_types_supported"] = [
            "code",
            "token",
            "id_token token",
            "urn:ietf:params:oauth:grant-type:device_code",
        ]

        # may be REQUIRED
        result["token_endpoint"] = urls_dict["get_tokens"]
        result["end_session_endpoint"] = urls_dict["end_session"]
        result["check_session_iframe"] = urls_dict["false"]

        # RECOMMENDED
        result["claims_supported"] = await self.get_claims()
        result["scopes_supported"] = ["openid", "email", "profile"]
        result["registration_endpoint"] = urls_dict["false"]
        result["userinfo_endpoint"] = urls_dict["get_userinfo"]

        # OPTIONAL

        result["grant_types_supported"] = [
            "authorization_code",
            "refresh_token",
            "client_credentials",
            "urn:ietf:params:oauth:grant-type:device_code",
        ]

        return result

    async def get_jwks(self) -> dict[str, Any]:
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
