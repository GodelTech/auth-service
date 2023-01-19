from src.data_access.postgresql.tables.client import Client
from src.data_access.postgresql.tables.users import UserClaim
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant


class WellKnownServies:
    def get_list_of_types(
        self, list_of_types: list = [("Not ready yet", "")]
    ) -> list:
        return [claim[0] for claim in list_of_types]

    def get_all_urls(self, result):
        return {
            route.name: result["issuer"] + route.path
            for route in self.request.app.routes
        } | {"false": "/ Not ready yet"}

    async def get_openid_configuration(
        self,
    ) -> dict:

        # For key description: https://ldapwiki.com/wiki/Openid-configuration
        # REQUIRED
        result = {
            "issuer": str(self.request.url).replace(
                "/.well-known/openid-configuration", ""
            )
        }

        urls_dict = self.get_all_urls(result)

        result["jwks_uri"] = urls_dict["false"]
        result["authorization_endpoint"] = urls_dict["get_authorize"]
        result[
            "id_token_signing_alg_values_supported"
        ] = self.get_list_of_types()
        result["subject_types_supported"] = self.get_list_of_types()
        result["response_types_supported"] = self.get_list_of_types()

        # may be REQUIRED
        result["token_endpoint"] = urls_dict['get_tokens']
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
        result["frontchannel_logout_session_supported"] = False  # i don't know
        result["frontchannel_logout_supported"] = False  # i don't know
        result["op_tos_uri"] = urls_dict["false"]
        result["op_policy_uri"] = urls_dict["false"]
        result["require_request_uri_registration"] = False  # i don't know
        result["request_uri_parameter_supported"] = False  # i don't know
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
        result["grant_types_supported"] = self.get_list_of_types(PersistentGrant.TYPES_OF_GRANTS)
        result["response_modes_supported"] = self.get_list_of_types()
        # result[""] = urls_dict['false']

        return result
