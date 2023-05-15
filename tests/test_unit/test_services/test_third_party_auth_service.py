import json
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthInvalidStateError,
    ThirdPartyAuthProviderInvalidRequestDataError,
    UnsupportedThirdPartyAuthProviderError,
)
from src.business_logic.third_party_auth.factory import (
    ThirdPartyAuthServiceFactory,
)
from src.business_logic.third_party_auth.interfaces import (
    ThirdPartyAuthServiceProtocol,
)
from src.business_logic.third_party_auth.service_impls import (
    GithubAuthService,
    GitlabAuthService,
    GoogleAuthService,
    LinkedinAuthService,
    MicrosoftAuthService,
)
from src.business_logic.third_party_auth.validators import (
    StateValidator,
    StateValidatorBase,
)
from tests.test_unit.fixtures import (
    state_request_model,
    third_party_access_token_request_model,
)


@pytest.fixture
def state_validator_base_with_mocked_dependencies(
    third_party_oidc_repository_mock,
):
    state_validator = StateValidatorBase(
        third_party_oidc_repo=third_party_oidc_repository_mock
    )
    yield state_validator
    del state_validator


@pytest.fixture
def state_validator_with_mocked_dependencies(third_party_oidc_repository_mock):
    state_validator = StateValidator(
        third_party_oidc_repo=third_party_oidc_repository_mock
    )
    yield state_validator
    del state_validator


@pytest.fixture
def third_party_auth_service_factory_with_mocked_dependencies(
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    factory = ThirdPartyAuthServiceFactory(
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield factory
    del factory


@pytest_asyncio.fixture
def github_auth_service_with_mocked_dependencies(
    state_validator_with_mocked_dependencies,
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    github_auth_service = GithubAuthService(
        state_validator=state_validator_with_mocked_dependencies,
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield github_auth_service
    del github_auth_service


@pytest_asyncio.fixture
def gitlab_auth_service_with_mocked_dependencies(
    state_validator_with_mocked_dependencies,
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    gitlab_auth_service = GitlabAuthService(
        state_validator=state_validator_with_mocked_dependencies,
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield gitlab_auth_service
    del gitlab_auth_service


@pytest_asyncio.fixture
def google_auth_service_with_mocked_dependencies(
    state_validator_with_mocked_dependencies,
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    google_auth_service = GoogleAuthService(
        state_validator=state_validator_with_mocked_dependencies,
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield google_auth_service
    del google_auth_service


@pytest_asyncio.fixture
def microsoft_auth_service_with_mocked_dependencies(
    state_validator_with_mocked_dependencies,
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    microsoft_auth_service = MicrosoftAuthService(
        state_validator=state_validator_with_mocked_dependencies,
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield microsoft_auth_service
    del microsoft_auth_service


@pytest_asyncio.fixture
def linkedin_auth_service_with_mocked_dependencies(
    state_validator_with_mocked_dependencies,
    client_repository_mock,
    user_repository_mock,
    persistent_grant_repository_mock,
    third_party_oidc_repository_mock,
    async_http_client_mock,
):
    linkedin_auth_service = LinkedinAuthService(
        state_validator=state_validator_with_mocked_dependencies,
        client_repo=client_repository_mock,
        user_repo=user_repository_mock,
        persistent_grant_repo=persistent_grant_repository_mock,
        oidc_repo=third_party_oidc_repository_mock,
        async_http_client=async_http_client_mock,
    )
    yield linkedin_auth_service
    del linkedin_auth_service


class TestThirdPartyAuthServiceFactory:
    @pytest.fixture(autouse=True)
    def setup(self, third_party_auth_service_factory_with_mocked_dependencies):
        self.factory = (
            third_party_auth_service_factory_with_mocked_dependencies
        )

    def test_register_factory(self):
        self.factory._register_factory("test", GithubAuthService)
        assert (
            self.factory._provider_name_to_service["test"] == GithubAuthService
        )
        del self.factory._provider_name_to_service["test"]

    def test_get_service_impl(self):
        self.factory._register_factory("test", GithubAuthService)
        service_impl = self.factory.get_service_impl("test")
        assert isinstance(service_impl, GithubAuthService)
        assert isinstance(service_impl, ThirdPartyAuthServiceProtocol)
        del self.factory._provider_name_to_service["test"]

    def test_get_service_impl_with_unsupported_provider(self):
        with pytest.raises(UnsupportedThirdPartyAuthProviderError):
            self.factory.get_service_impl("test")

    @pytest.mark.asyncio
    @patch(
        "src.business_logic.third_party_auth.factory.StateValidatorBase",
        return_value=AsyncMock(StateValidatorBase),
    )
    async def test_create_provider_state(self, mocked_state_validator):
        state_validator_instance = mocked_state_validator.return_value
        await self.factory.create_provider_state("state")

        # check if StateValidator was initialized and called with state
        mocked_state_validator.assert_called_once_with(self.factory._oidc_repo)
        state_validator_instance.assert_called_once_with("state")
        self.factory._oidc_repo.create_state.assert_called_once_with("state")


@pytest.mark.asyncio
class TestStateValidatorBase:
    @pytest.fixture(autouse=True)
    def setup(self, state_validator_base_with_mocked_dependencies):
        self.state_validator = state_validator_base_with_mocked_dependencies

    async def test_state_validator_base(self):
        state = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        await self.state_validator(state)

    async def test_state_validator_base_with_truthy_is_state(self):
        state = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        self.state_validator._third_party_oidc_repo.is_state.return_value = (
            True
        )
        with pytest.raises(
            ThirdPartyAuthInvalidStateError, match="State already exists."
        ):
            await self.state_validator(state)

    async def test_state_validator_base_with_invalid_state(self):
        self.state_validator._third_party_oidc_repo.is_state.return_value = (
            True
        )
        with pytest.raises(
            ThirdPartyAuthInvalidStateError, match="State already exists."
        ):
            await self.state_validator(state="invalid")


@pytest.mark.asyncio
class TestStateValidator:
    @pytest.fixture(autouse=True)
    def setup(self, state_validator_with_mocked_dependencies):
        self.state_validator = state_validator_with_mocked_dependencies

    async def test_state_validator(self):
        state = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        self.state_validator._third_party_oidc_repo.is_state.return_value = (
            True
        )
        await self.state_validator(state)
        self.state_validator._third_party_oidc_repo.delete_state.assert_called_once_with(
            state
        )

    async def test_state_validator_with_falsy_is_state(self):
        state = "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        with pytest.raises(
            ThirdPartyAuthInvalidStateError, match="State does not exist."
        ):
            await self.state_validator(state)


@pytest.mark.asyncio
class TestGithubAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, github_auth_service_with_mocked_dependencies):
        self.auth_service = github_auth_service_with_mocked_dependencies

    async def test_form_parameters_data(
        self, third_party_access_token_request_model
    ):
        result = await self.auth_service._form_parameters_data(
            third_party_access_token_request_model, "github"
        )
        assert result == {
            "client_id": "test_client",
            "client_secret": "test_secret",
            "redirect_uri": "test_redirect_uri",
            "code": "test_code",
            "grant_type": "authorization_code",
        }

    async def test_update_redirect_url(
        self, third_party_access_token_request_model
    ):
        result = await self.auth_service._update_redirect_url(
            third_party_access_token_request_model,
            redirect_url="http://www.test.com/test",
        )
        assert result == "http://www.test.com/test&state=test_state"

    async def test_update_redirect_url_without_state(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = None
        result = await self.auth_service._update_redirect_url(
            third_party_access_token_request_model,
            redirect_url="http://www.test.com/test",
        )
        assert result == "http://www.test.com/test"

    @patch(
        "src.business_logic.third_party_auth.service_impls.github.GithubAuthService._form_parameters_data",
        return_value={"param1": "test"},
    )
    async def test_get_access_token(
        self,
        mocked_form_parameters_data,
        third_party_access_token_request_model,
    ):
        access_token = "test_token"
        self.auth_service._async_http_client.request.return_value.content = (
            json.dumps({"access_token": access_token})
        )
        result = await self.auth_service._get_access_token(
            third_party_access_token_request_model,
            token_url="https://www.test.com/token/",
            provider_name="test_provider",
        )
        assert result == access_token

    @patch(
        "src.business_logic.third_party_auth.service_impls.github.GithubAuthService._form_parameters_data",
        return_value={"param1": "test"},
    )
    async def test_get_access_token_with_error_response(
        self,
        mocked_form_parameters_data,
        third_party_access_token_request_model,
    ):
        self.auth_service._async_http_client.request.return_value.content = (
            json.dumps({"error": "test_error"})
        )
        with pytest.raises(ThirdPartyAuthProviderInvalidRequestDataError):
            await self.auth_service._get_access_token(
                third_party_access_token_request_model,
                token_url="https://www.test.com/token/",
                provider_name="test_provider",
            )

    @patch(
        "src.business_logic.third_party_auth.service_impls.github.GithubAuthService._get_access_token",
        return_value="access_token",
    )
    async def test_get_username(
        self, mocked_access_token, third_party_access_token_request_model
    ):
        username = "test_login"
        self.auth_service._async_http_client.request.return_value.content = (
            json.dumps({"login": username})
        )
        result = await self.auth_service._get_username(
            third_party_access_token_request_model,
            username_type="login",
            provider_name="test_provider",
        )
        assert result == username

    async def test_create_user_if_not_exists(self):
        username, provider_name = "test_username", "test_provider"
        await self.auth_service._create_user_if_not_exists(
            username, provider_name
        )
        self.auth_service._user_repo.exists_user.assert_called_once_with(
            username
        )
        self.auth_service._oidc_repo.get_id_by_provider_name.assert_called_once_with(
            provider_name
        )
        self.auth_service._user_repo.create.assert_called_once_with(
            username=username, identity_provider_id="test_id"
        )

    @patch(
        "src.business_logic.third_party_auth.service_impls.mixins.time.time",
        return_value=123,
    )
    async def test_create_grant(self, third_party_access_token_request_model):
        username_type, provider_name = ("login", "test_provider")
        username = ("test_user",)
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._get_username = AsyncMock(return_value=username)
        self.auth_service._create_user_if_not_exists = AsyncMock(
            return_value=None
        )
        self.auth_service._secret_code = "test_secret"
        await self.auth_service._create_grant(
            request_data=third_party_access_token_request_model,
            username_type=username_type,
            provider_name=provider_name,
        )
        self.auth_service._get_username.assert_called_once_with(
            request_data=third_party_access_token_request_model,
            username_type=username_type,
            provider_name=provider_name,
        )
        self.auth_service._create_user_if_not_exists.assert_called_once_with(
            username, provider_name
        )
        self.auth_service._client_repo.get_auth_code_lifetime_by_client.assert_called_once_with(
            "test_client"
        )
        self.auth_service._user_repo.get_user_id_by_username.assert_called_once_with(
            username
        )
        self.auth_service._persistent_grant_repo.create.assert_called_once_with(
            client_id="test_client",
            grant_data="test_secret",
            user_id="test_user",
            grant_type="authorization_code",
            expiration_time=183,  # sum of auth_code_lifetime mocked as 60 and time.time mocked as 123
        )

    async def test_get_redirect_url(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._secret_code = "secret_code"
        self.auth_service._state_validator = AsyncMock(return_value=None)
        self.auth_service._create_grant = AsyncMock(return_value=None)
        result = await self.auth_service.get_redirect_url(
            third_party_access_token_request_model
        )
        assert (
            result == "https://www.google.com/?code=secret_code"
            "&state=2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        )


@pytest.mark.asyncio
class TestGitlabAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, gitlab_auth_service_with_mocked_dependencies):
        self.auth_service = gitlab_auth_service_with_mocked_dependencies

    async def test_get_redirect_url(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._secret_code = "secret_code"
        self.auth_service._state_validator = AsyncMock(return_value=None)
        self.auth_service._create_grant = AsyncMock(return_value=None)
        result = await self.auth_service.get_redirect_url(
            third_party_access_token_request_model
        )
        assert (
            result == "https://www.google.com/?code=secret_code"
            "&state=2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        )


@pytest.mark.asyncio
class TestGoogleAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, google_auth_service_with_mocked_dependencies):
        self.auth_service = google_auth_service_with_mocked_dependencies

    async def test_get_redirect_url(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._secret_code = "secret_code"
        self.auth_service._state_validator = AsyncMock(return_value=None)
        self.auth_service._create_grant = AsyncMock(return_value=None)
        result = await self.auth_service.get_redirect_url(
            third_party_access_token_request_model
        )
        assert (
            result == "https://www.google.com/?code=secret_code"
            "&state=2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        )


@pytest.mark.asyncio
class TestLinkedinAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, linkedin_auth_service_with_mocked_dependencies):
        self.auth_service = linkedin_auth_service_with_mocked_dependencies

    async def test_get_redirect_url(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._secret_code = "secret_code"
        self.auth_service._state_validator = AsyncMock(return_value=None)
        self.auth_service._create_grant = AsyncMock(return_value=None)
        result = await self.auth_service.get_redirect_url(
            third_party_access_token_request_model
        )
        assert (
            result == "https://www.google.com/?code=secret_code"
            "&state=2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        )


@pytest.mark.asyncio
class TestMicrosoftAuthService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, microsoft_auth_service_with_mocked_dependencies):
        self.auth_service = microsoft_auth_service_with_mocked_dependencies

    @patch(
        "src.business_logic.third_party_auth.service_impls.microsoft.MicrosoftAuthService._form_parameters_data",
        return_value={"param1": "test"},
    )
    async def test_get_access_token(
        self,
        mocked_form_parameters_data,
        third_party_access_token_request_model,
    ):
        access_token = "test_token"
        self.auth_service._async_http_client.request.return_value.content = (
            json.dumps({"access_token": access_token})
        )
        result = await self.auth_service._get_access_token(
            third_party_access_token_request_model,
            token_url="https://www.test.com/token/",
            provider_name="test_provider",
        )
        assert result == access_token

    @patch(
        "src.business_logic.third_party_auth.service_impls.microsoft.MicrosoftAuthService._form_parameters_data",
        return_value={"param1": "test"},
    )
    async def test_get_access_token_with_error_response(
        self,
        mocked_form_parameters_data,
        third_party_access_token_request_model,
    ):
        self.auth_service._async_http_client.request.return_value.content = (
            json.dumps({"error": "test_error"})
        )
        with pytest.raises(ThirdPartyAuthProviderInvalidRequestDataError):
            await self.auth_service._get_access_token(
                third_party_access_token_request_model,
                token_url="https://www.test.com/token/",
                provider_name="test_provider",
            )

    async def test_get_redirect_url(
        self, third_party_access_token_request_model
    ):
        third_party_access_token_request_model.state = (
            "2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg"
            "!_!test_client!_!https://www.google.com/"
        )
        self.auth_service._secret_code = "secret_code"
        self.auth_service._state_validator = AsyncMock(return_value=None)
        self.auth_service._create_grant = AsyncMock(return_value=None)
        result = await self.auth_service.get_redirect_url(
            third_party_access_token_request_model
        )
        assert (
            result == "https://www.google.com/?code=secret_code"
            "&state=2y0M9hbzcCv5FZ28ZxRu2upCBI6LkS9conRvkVQPuTg!_!test_client!_!https://www.google.com/"
        )
