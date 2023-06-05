import datetime

import pytest_asyncio
from pydantic import SecretStr

from src.business_logic.services.jwt_token import JWTService
from src.presentation.api.models import (
    DeviceCancelModel,
    DeviceRequestModel,
    DeviceUserCodeModel,
    StateRequestModel,
    ThirdPartyGoogleRequestModel,
    ThirdPartyMicrosoftRequestModel,
    ThirdPartyOIDCRequestModel,
)
from src.presentation.api.models.authorization import (
    DataRequestModel,
    RequestModel,
)
from src.presentation.api.models.endsession import RequestEndSessionModel

TEST_VALIDATE_PASSWORD = [
    (
        SecretStr("test_password"),
        "$2b$12$rNqlpYZ51ilkRAr5uH5SfOAPUeQUrnclub8r3XNTQh6pS7lBqXnEi",
    ),
    (
        SecretStr("abra_vadaBra"),
        "$2b$12$dszlwCsMRY29mNuIAgMrEuZt412OslAl3KN8m95Ze.X7eCYnexoce",
    ),
    (
        SecretStr("fhfy$%_mkLKvbh67eT"),
        "$2b$12$4dyIxC1keM0taJ6wetY8JOIAW2UOZNYT.Vhz5YoVPnpeqSo.pOmsO",
    ),
    (SecretStr("test_password"), "$2b$12$rNqlpYZ51ilkRAr5uH5SfOAPUe"),
    (SecretStr("abra_vadaBra"), "$2b$12$dszlwCsMRY29mNuIAgMrEuZt412OslA"),
    (SecretStr("fhfy$%_mkLKvbh67eT"), "$2b$12$4dyIxC1keM0taJ6wetY8JOIAW2"),
]

DEFAULT_CLIENT = {
    "client_id": "default_test_client",
    "absolute_refresh_token_lifetime": 3600,
    "access_token_lifetime": 3600,
    "access_token_type_id": 1,
    "allow_access_token_via_browser": False,
    "allow_offline_access": False,
    "allow_plain_text_pkce": False,
    "allow_remember_consent": True,
    "always_include_user_claims_id_token": False,
    "always_send_client_claims": False,
    "authorization_code_lifetime": 300,
    "device_code_lifetime": 600,
    "client_name": "TestClient",
    "client_uri": "test_uri",
    "enable_local_login": True,
    "enabled": True,
    "identity_token_lifetime": 300,
    "include_jwt_id": False,
    "logo_uri": "test_logo_uri",
    "logout_session_required": False,
    "logout_uri": "test_logout_uri",
    "prefix_client_claims": "test_",
    "protocol_type_id": 1,
    "refresh_token_expiration_type_id": 1,
    "refresh_token_usage_type_id": 2,
    "require_client_secret": False,
    "require_consent": False,
    "require_pkce": False,
    "sliding_refresh_token_lifetime": 1296000,
    "update_access_token_claims_on_refresh": False,
}

DEFAULT_USER = {
    "email": "test_user@tes.com",
    "email_confirmed": True,
    "password_hash_id": 1,
    "security_stamp": "security_stamp",
    "phone_number": "4567736574",
    "phone_number_confirmed": False,
    "two_factors_enabled": True,
    "lockout_end_date_utc": datetime.datetime.utcnow(),
    "lockout_enabled": True,
    "access_failed_count": 0,
    "username": "DefaultTestClient",
}

DEFAULT_USER_CLAIMS = [
    {"User": 1, "claim_type": "given_name", "claim_value": "Tony"},
    {"User": 1, "claim_type": "family_name", "claim_value": "Stark"},
    {"User": 1, "claim_type": "nickname", "claim_value": "IronMan"},
]


@pytest_asyncio.fixture
def authorization_get_request_model() -> RequestModel:
    request_model = RequestModel(
        client_id="test_client",
        response_type="code",
        scope="openid",
        redirect_uri="http://127.0.0.1:8888/callback/",
        state="state",
        response_mode="mode",
        nonce="test_data",
        display="test_data",
        prompt="test_data",
        max_age=3600,
        ui_locales="test_data",
        id_token_hint="test_data",
        login_hint="test_data",
        acr_values="test_data",
        user_code="test_data",
    )
    return request_model


@pytest_asyncio.fixture
def auth_post_request_model() -> DataRequestModel:
    request_model = DataRequestModel(
        client_id="test_client",
        response_type="code",
        scope="openid",
        redirect_uri="https://test.com/redirect",
        state="test_state",
        response_mode="mode",
        nonce="test_data",
        display="test_data",
        prompt="test_data",
        max_age=3600,
        ui_locales="test_data",
        id_token_hint="test_data",
        login_hint="test_data",
        acr_values="test_data",
        username="test_user",
        password=SecretStr("test_password"),
    )
    return request_model


@pytest_asyncio.fixture
def device_cancel_model() -> DeviceCancelModel:
    cancel_model = DeviceCancelModel(
        client_id="test_client",
        scope="gcp-api%20IdentityServerApi&grant_type=urn:ietf:params:oauth:grant-type:device_code&"
        "client_id=test_client&client_secret=65015c5e-c865-d3d4-3ba1-3abcb4e65500&"
        "password=test_password&username=TestClient&user_code=user_code",
    )
    return cancel_model


@pytest_asyncio.fixture
def device_user_code_model() -> DeviceUserCodeModel:
    user_code_model = DeviceUserCodeModel(user_code="GHJKTYUI")
    return user_code_model


@pytest_asyncio.fixture
def device_request_model() -> DeviceRequestModel:
    request_model = DeviceRequestModel(client_id="test_client")
    return request_model


service = JWTService()

TOKEN_HINT_DATA = {
    "sub": 3,
    "client_id": "santa",
    "data": "secret_code",
    "type": "code",
}

SHORT_TOKEN_HINT_DATA = {"sub": 3, "data": "secret_code", "type": "code"}


class TokenHint:
    sv = JWTService()

    @classmethod
    async def get_token_hint(cls) -> str:
        token_hint = await cls.sv.encode_jwt(payload=TOKEN_HINT_DATA)
        return token_hint

    @classmethod
    async def get_short_token_hint(cls) -> str:
        short_token_hint = await cls.sv.encode_jwt(
            payload=SHORT_TOKEN_HINT_DATA
        )
        return short_token_hint


@pytest_asyncio.fixture
async def end_session_request_model() -> RequestEndSessionModel:
    tk_hint = TokenHint()
    token_hint = await tk_hint.get_token_hint()
    request_model = RequestEndSessionModel(
        id_token_hint=token_hint,
        post_logout_redirect_uri="http://thompson-chung.com/",
        state="test_state",
    )
    return request_model


@pytest_asyncio.fixture
async def third_party_oidc_request_model() -> ThirdPartyOIDCRequestModel:
    oidc_request_model = ThirdPartyOIDCRequestModel(
        code="test_code", state="test_state"
    )
    return oidc_request_model


@pytest_asyncio.fixture
async def state_request_model() -> StateRequestModel:
    request_model = StateRequestModel(state="some_crazy_state")
    return request_model


@pytest_asyncio.fixture
async def third_party_google_request_model() -> ThirdPartyGoogleRequestModel:
    oidc_request_model = ThirdPartyGoogleRequestModel(
        code="test_code", state="test_state", scope="test_scope"
    )
    return oidc_request_model


@pytest_asyncio.fixture
async def third_party_microsoft_request_model() -> ThirdPartyMicrosoftRequestModel:
    oidc_request_model = ThirdPartyMicrosoftRequestModel(
        code="test_code", state="test_state"
    )
    return oidc_request_model
