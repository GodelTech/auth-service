import pytest
import mock
from sqlalchemy import insert

from src.main import app
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.authorisation import AuthorisationService
from src.data_access.postgresql.errors.password import WrongPasswordError
from src.data_access.postgresql.errors.client import ClientNotFoundError
from src.data_access.postgresql.repositories.client import ClientRepository, Client
from src.business_logic.dependencies import get_repository
from tests.api.test_routes.test_database import engine
from src.business_logic.services.userinfo import UserInfoServies
from src.data_access.postgresql.repositories.user import UserRepository
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.well_known import WellKnownServies


class RequestMock():
    authorization = 0


@pytest.mark.asyncio
class TestUserInfoServiece():

    @classmethod
    def setup_class(cls):
        request = RequestMock()
        request.authorization = 1
        cls.uis = UserInfoServies()
        cls.uis.request = request
        cls.uis.user_repo = get_repository(UserRepository)
        cls.uis.user_repo = cls.uis.user_repo()

    async def test_get_user_info_and_get_user_info_jwt(self):

        def new_decode_token(*args, **kwargs):
            return {"sub": 1}

        async def new_get_user_info_dict(*args, **kwargs):
            return {'name': 'Danya',
                    'given_name': 'Ibragim',
                    'family_name': 'Krats',
                    'middle_name': '-el-',
                    'nickname': 'Nagibator2000',
                    }

        with mock.patch.object(UserRepository, "get_claims", new=new_get_user_info_dict):
            with mock.patch.object(JWTService, "decode_token", new=new_decode_token):
                expected_part_one = {"sub": str(new_decode_token()["sub"])}
                expected_part_two = await new_get_user_info_dict()
                expected = expected_part_one | expected_part_two
                result = await self.uis.get_user_info()
                result_jwt = await self.uis.get_user_info_jwt()

                assert expected == result
                assert self.uis.jwt.encode_jwt(expected) == result_jwt


@pytest.mark.asyncio
class TestJWTServiece():

    @classmethod
    def setup_class(cls):
        cls.jwt = JWTService()

    def test_encode_and_decode(self):
        token = self.jwt.encode_jwt(payload={"sub": 123, "name": "Danya"})
        assert token.count('.') == 2

        for tkn in (token, "Bearer " + token):
            decoded_dict = self.jwt.decode_token(tkn)
            assert type(decoded_dict) == dict
            assert decoded_dict["sub"] == 123
            assert decoded_dict["name"] == "Danya"


@pytest.mark.asyncio
class TestWellKnownServies():

    @classmethod
    def setup_class(cls):
        cls.wks = WellKnownServies()
        cls.wks.request = RequestMock()
        cls.wks.request.url = '/localhost/.well-known/openid-configuration'
    
    def new_get_all_urls(self,*args, **kwargs):
        return {'openapi': 'http://127.0.0.1:800...enapi.json', 'swagger_ui_html': 'http://127.0.0.1:8000/docs', 'swagger_ui_redirect': 'http://127.0.0.1:800...2-redirect', 'redoc_html': 'http://127.0.0.1:8000/redoc', 'get_authorize': 'http://127.0.0.1:800...authorize/',
                                      'post_authorize': 'http://127.0.0.1:800...authorize/', 'get_userinfo': 'http://127.0.0.1:800.../userinfo/', 'get_userinfo_jwt': 'http://127.0.0.1:800...erinfo/jwt', 'get_default_token': 'http://127.0.0.1:800...ault_token', 'get_openid_configuration': 'http://127.0.0.1:800...figuration', 'false': '/ Not ready yet'}

    async def test_well_known_openid_cofig(self):
        with mock.patch.object(WellKnownServies, "get_all_urls", new=self.new_get_all_urls):
            result = await self.wks.get_openid_configuration()
            dict_of_parametrs_and_types = {"issuer": str,
                                        "jwks_uri": str,
                                        "authorization_endpoint": str,
                                        "token_endpoint": str,
                                        "id_token_signing_alg_values_supported": list,
                                        "subject_types_supported": list,
                                        "response_types_supported": list,
                                        "claims_supported": list,
                                        "scopes_supported": list,
                                        "registration_endpoint": str,
                                        "userinfo_endpoint": str,
                                        "frontchannel_logout_session_supported": bool,
                                        "frontchannel_logout_supported": bool,
                                        "end_session_endpoint": str,
                                        "check_session_iframe": str,
                                        "op_tos_uri": str,
                                        "op_policy_uri": str,
                                        "require_request_uri_registration": bool,
                                        "request_uri_parameter_supported": bool,
                                        "request_parameter_supported": bool,
                                        "claims_parameter_supported": bool,
                                        "ui_locales_supported": list,
                                        "claims_locales_supported": list,
                                        "service_documentation": list,
                                        "claim_types_supported": list,
                                        "display_values_supported": list,
                                        "token_endpoint_auth_signing_alg_values_supported": list,
                                        "token_endpoint_auth_methods_supported": list,
                                        "request_object_encryption_enc_values_supported": list,
                                        "request_object_encryption_alg_values_supported": list,
                                        "request_object_signing_alg_values_supported": list,
                                        "userinfo_encryption_enc_values_supported": list,
                                        "userinfo_encryption_alg_values_supported": list,
                                        "userinfo_signing_alg_values_supported": list,
                                        "id_token_encryption_enc_values_supported": list,
                                        "id_token_encryption_alg_values_supported": list,
                                        "acr_values_supported": list,
                                        "grant_types_supported": list,
                                        "response_modes_supported": list
                                        }
            
            for key in result.keys():
                assert type(result[key]) == dict_of_parametrs_and_types[key]
            
            KEYS_REQUIRED = ('issuer', 'jwks_uri', 'authorization_endpoint', 'token_endpoint',
                        'id_token_signing_alg_values_supported', 'subject_types_supported', 'response_types_supported')

            for key in KEYS_REQUIRED:
                assert key in result.keys() 

