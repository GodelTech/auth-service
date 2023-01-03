import datetime

import pytest_asyncio

from src.presentation.api.models.authorization import RequestModel

TEST_VALIDATE_PASSWORD = [
    (
        "test_password",
        "$2b$12$rNqlpYZ51ilkRAr5uH5SfOAPUeQUrnclub8r3XNTQh6pS7lBqXnEi",
    ),
    (
        "abra_vadaBra",
        "$2b$12$dszlwCsMRY29mNuIAgMrEuZt412OslAl3KN8m95Ze.X7eCYnexoce",
    ),
    (
        "fhfy$%_mkLKvbh67eT",
        "$2b$12$4dyIxC1keM0taJ6wetY8JOIAW2UOZNYT.Vhz5YoVPnpeqSo.pOmsO",
    ),
    ("test_password", "$2b$12$rNqlpYZ51ilkRAr5uH5SfOAPUe"),
    ("abra_vadaBra", "$2b$12$dszlwCsMRY29mNuIAgMrEuZt412OslA"),
    ("fhfy$%_mkLKvbh67eT", "$2b$12$4dyIxC1keM0taJ6wetY8JOIAW2"),
]

DEFAULT_CLIENT = {
    "client_id": "default_test_client",
    "absolute_refresh_token_lifetime": 3600,
    "access_token_lifetime": 3600,
    "access_token_type": "reference",
    "allow_access_token_via_browser": False,
    "allow_offline_access": False,
    "allow_plain_text_pkce": False,
    "allow_remember_consent": True,
    "always_include_user_claims_id_token": False,
    "always_send_client_claims": False,
    "authorisation_code_lifetime": 300,
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
    "protocol_type": "open_id_connect",
    "refresh_token_expiration": "absolute",
    "refresh_token_usage": "one_time_only",
    "require_client_secret": False,
    "require_consent": False,
    "require_pkce": False,
    "sliding_refresh_token_lifetime": 1296000,
    "update_access_token_claims_on_refresh": False,
}

DEFAULT_USER = {
    "email": "test_user@tes.com",
    "email_confirmed": True,
    "password_hash": "$2b$12$RAC7jWdNn8Fudxc4OhudkOPK0eeBBWjGd5Iyfzma5F8uv9xD.jx/6",
    "security_stamp": "security_stamp",
    "phone_number": "4567736574",
    "phone_number_confirmed": False,
    "two_factors_enabled": True,
    "lockout_end_date_utc": datetime.datetime.now(),
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
def authorization_request_model():
    request_model = RequestModel(
        client_id="test_client",
        response_type="code",
        scope="gcp-api%20IdentityServerApi&grant_type=password&client_id=test_client&client_secret"
        "=65015c5e-c865-d3d4-3ba1-3abcb4e65500&password=test_password&username=TestClient",
        redirect_uri="https://www.google.com/",
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
    )

    return request_model
