from business_logic.dto.open_id_config import OpenIdConfiguration
from src.business_logic.services.jwt_token import JWTService
from jwkest import long_to_base64, base64_to_long
import logging
from src.dyna_config import DOMAIN_NAME
from jwkest import base64_to_long, long_to_base64
from fastapi import Request
from src.business_logic.services.jwt_token import JWTService
from typing import Any, Union
from src.data_access.postgresql.repositories import WellKnownRepository
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class WellKnownService:
    """A class that provides a metadata that an OAuth 2.0 client can use to
    obtain the information needed to interact with an OAuth 2.0 authorization server
    including its endpoint locations and authorization server capabilities.

    More detalis about the functionality can be found in the
    [official documentation](https://www.rfc-editor.org/rfc/rfc8414)
    [openid connect discover 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)

    """

    def __init__(
        self, session: AsyncSession, wlk_repo: WellKnownRepository
    ) -> None:
        """Initialize the WellKnownService.

        Args:
            session (AsyncSession): The session object.
            wlk_repo (WellKnownRepository): The repository object.
        """
        self.request: Union[Request, Any] = None
        self.wlk_repo = wlk_repo
        self.session = session

    def get_list_of_types(
        self, list_of_types: list[Any] = [("Not ready yet", "")]
    ) -> list[str]:
        """Retrieves a list of types from a given list.

        Args:
            list_of_types (List[Any], optional): The list of types.
            Defaults to [("Not ready yet", "")] as it is not implemented yet.

        Returns:
            List[str]: The list of types.
        """
        return [claim[0] for claim in list_of_types]

    def get_all_urls(self, result: dict[str, Any]) -> dict[str, Any]:
        """Retrieves all URLs from the request app routes.

        Args:
            result (Dict[str, Any]): The result dictionary.

        Returns:
            Dict[str, Any]: The dictionary of URLs containing all available endpoints.
        """
        if self.request is None:
            raise ValueError
        return {
            route.name: result["issuer"] + route.path
            for route in self.request.app.routes
        } | {"false": "/ Not ready yet"}

    def get_algorithms(self) -> list[str]:
        """Retrieves a list of algorithms from the JWTService.

        Returns:
            List[str]: The list of algorithms, currently contains only "RS256".
        """
        return JWTService().algorithms

    async def get_claims(self) -> list[str]:
        """Retrieves the user claim types from the repository.

        Returns:
            List[str]: The list of user claim types. Contains user`s parameters
            like "name", "family_name", "gender", and the like.
        """
        result = await self.wlk_repo.get_user_claim_types()
        return result

    async def get_grant_types(self) -> list[str]:
        """Retrieves the grant types from the repository.

        Returns:
            List[str]: The list of grant types. Currently it contains "authorization_code",
            "refresh_token", "client_credentials", "urn:ietf:params:oauth:grant-type:device_code".
        """
        result = await self.wlk_repo.get_grant_types()
        return result

    async def get_openid_configuration(
        self,
    ) -> OpenIdConfiguration:
        """
        Retrieves the OpenID configuration class containing metadata decribing authorization servers
        configuration.

        Returns:
            OpenIdConfiguration: The OpenID configuration in the form of pydantic model.
            Required parameters:
            - issuer - The authorization server's issuer identifier, which is a URL that uses the "https" scheme and has no query or fragment
            components.  Authorization server metadata is published at a location that is ".well-known".
            - authorization_endpoint - URL of the authorization server's authorization endpoint.
            - token_endpoint -  URL of the authorization server's token endpoint.
            - response_types_supported - JSON array containing a list of the OAuth 2.0
            "response_type" values that this authorization server supports.
            - id_token_signing_alg_values_supported - JSON array containing a list of
            the JWS signing algorithms (alg values) supported by the OP for the ID Token to encode the Claims in a JWT.
            - subject_types_supported - JSON array containing a list of the Subject Identifier types that this OP supports.
            Not required parameters:
            - claims_supported - JSON array containing a list of the Claim Names of the Claims that the OpenID Provider is able to supply values for.
            - scopes_supported -  JSON array containing a list of the OAuth 2.0 scope values that this server supports.
            - registration_endpoint - URL of the OP's Dynamic Client Registration Endpoint.
            - userinfo_endpoint - URL of the OP's UserInfo Endpoint.
            - end_session_endpoint - URL of the authorization server's endsession endpoint.
            - check_session_iframe - parameter is used to enable the OpenID Connect session management feature.
            - grant_types_supported - JSON array containing a list of the OAuth 2.0 Grant Type values that this OP supports.

        """
        if self.request is None:
            raise ValueError

        # REQUIRED
        result: dict[str, Any] = {}
        result["issuer"] = DOMAIN_NAME

        urls_dict = self.get_all_urls(result)

        result["jwks_uri"] = urls_dict["get_jwks"]
        result["authorization_endpoint"] = urls_dict["get_authorize"]
        result["id_token_signing_alg_values_supported"] = self.get_algorithms()
        result["subject_types_supported"] = ["public"]
        result["response_types_supported"] = [
            "code",
            "token",
            "id_token token",
            "urn:ietf:params:oauth:grant-type:device_code",
        ]
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
        result_model = OpenIdConfiguration(**result)

        return result_model

    async def get_jwks(self) -> dict[str, Any]:
        """Retrieves the JWKS (JSON Web Key Set).

        Returns:
            Dict[str, Any]: The JWKS dictionary. Contains properties:
            - kty - The family of cryptographic algorithms used with the key.
            - alg - The specific cryptographic algorithm used with the key.
            - use - How the key is meant to be used.
            - n - The modulus for the RSA public key.
            - e - The exponent for the RSA public key.

        """
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
