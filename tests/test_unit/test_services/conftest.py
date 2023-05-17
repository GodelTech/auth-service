from unittest.mock import AsyncMock, MagicMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession


import pytest
import pytest_asyncio


@pytest_asyncio.fixture
def client_repository_mock():
    client_repo = AsyncMock()
    client_repo.validate_client_redirect_uri.return_value = None
    # Create a mock object for the client with an 'id' attribute
    mock_client = MagicMock(id=1)
    client_repo.get_client_by_client_id.return_value = mock_client
    client_repo.get_client_scopes_by_client_id.return_value = "openid"
    client_repo.get_auth_code_lifetime_by_client.return_value = 60
    yield client_repo
    del client_repo


@pytest_asyncio.fixture
def user_repository_mock():
    user_repo = AsyncMock()
    user_repo.get_hash_password.return_value = (
        "hashed_password",
        1,
    )
    user_repo.exists_user.return_value = False
    user_repo.create.return_value = None
    user_repo.get_user_id_by_username.return_value = "test_user"
    yield user_repo
    del user_repo


@pytest_asyncio.fixture
def persistent_grant_repository_mock():
    persistent_grant_repo = AsyncMock()
    persistent_grant_repo.create.return_value = None
    yield persistent_grant_repo
    del persistent_grant_repo


@pytest_asyncio.fixture
def device_repository_mock():
    device_repo = AsyncMock()
    device_repo.delete_by_user_code.return_value = None
    mock_device = MagicMock(device_code=MagicMock)
    mock_device.device_code.value = 1
    device_repo.get_device_by_user_code.return_value = mock_device
    yield device_repo
    del device_repo


@pytest_asyncio.fixture
def third_party_oidc_repository_mock():
    third_party_oidc_repo = AsyncMock()
    third_party_oidc_repo.create_state.return_value = None
    third_party_oidc_repo.is_state.return_value = False
    third_party_oidc_repo.delete_state.return_value = None
    third_party_oidc_repo.get_credentials_by_provider_name.return_value = (
        "test_client",
        "test_secret",
        "test_redirect_uri",
    )
    third_party_oidc_repo.get_external_links_by_provider_name.return_value = (
        "token_url",
        "user_info_url",
    )
    third_party_oidc_repo.get_id_by_provider_name.return_value = "test_id"
    yield third_party_oidc_repo
    del third_party_oidc_repo


@pytest_asyncio.fixture
def async_http_client_mock():
    client = AsyncMock()
    yield client
    del client


@pytest_asyncio.fixture
def async_session_mock():
    session = AsyncSession()
    yield session
    del session


@pytest.fixture
def password_hash_mock():
    return Mock()


@pytest_asyncio.fixture
def jwt_service_mock():
    return AsyncMock()
