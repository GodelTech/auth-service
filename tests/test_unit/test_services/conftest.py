import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, Mock


@pytest_asyncio.fixture
def client_repository_mock():
    client_repo = AsyncMock()
    client_repo.validate_client_redirect_uri.return_value = None
    # Create a mock object for the client with an 'id' attribute
    mock_client = MagicMock(id=1)
    client_repo.get_client_by_client_id.return_value = mock_client
    client_repo.get_client_scopes_by_client_id.return_value = "openid"
    yield client_repo
    del client_repo


@pytest_asyncio.fixture
def user_repository_mock():
    user_repo = AsyncMock()
    user_repo.get_hash_password.return_value = (
        "hashed_password",
        1,
    )
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


@pytest.fixture
def password_hash_mock():
    return Mock()


@pytest_asyncio.fixture
def jwt_service_mock():
    return AsyncMock()
