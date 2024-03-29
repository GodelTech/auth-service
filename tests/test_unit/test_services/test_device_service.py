import pytest
from typing import Any
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserCodeNotFoundError,
)
from tests.test_unit.fixtures import device_cancel_model, device_user_code_model, device_request_model
from src.dyna_config import DOMAIN_NAME
from src.business_logic.services.device_auth import DeviceService, DeviceCancelModel, DeviceUserCodeModel, DeviceRequestModel

@pytest.mark.asyncio
class TestDeviceService:

    async def test_validate_client(self, device_service: DeviceService) -> None:
        service = device_service
        client = await service._validate_client(client_id="test_client")
        assert client is True

    async def test_validate_client_not_exist(self, device_service: DeviceService) -> None:
        service = device_service
        with pytest.raises(ClientNotFoundError):
            await service._validate_client(
                client_id="bla1bla_io"
            )

    async def test_validate_user_code(self, device_service: DeviceService) -> None:
        service = device_service
        await service.device_repo.create(
            client_id="test_client",
            device_code="urn:ietf:params:oauth:grant-type:device_code",
            user_code="user_code",
            verification_uri="some_uri",
            verification_uri_complete="complete_uri",
            expires_in=600,
            interval=5,
        )
        user_code = await service._validate_user_code(user_code="user_code")
        assert user_code is True
        await service.device_repo.delete_by_user_code(user_code="user_code")

    async def test_validate_user_code_not_exist(self, device_service: DeviceService) -> None:
        service = device_service
        with pytest.raises(UserCodeNotFoundError):
            await service._validate_user_code(user_code="fgt345&uhy")

    async def test_parse_scope_data(self, device_service: DeviceService) -> None:
        expected_password = "BestOfTheBest"
        expected_client_id = "tony_stark"
        expected_username = "IronMan"

        to_parse = "gcp-api%20IdentityServerApi&client_id=tony_stark&password=BestOfTheBest&username=IronMan"
        result = await device_service._parse_scope_data(to_parse)
        assert result["client_id"] == expected_client_id
        assert result["password"] == expected_password
        assert result["username"] == expected_username

    async def test_parse_empty_scope(self, device_service: DeviceService) -> None:
        to_parse = ""
        result = await device_service._parse_scope_data(to_parse)
        assert result == {}

    async def test_parse_scope_without_separator(self, device_service: DeviceService) -> None:
        expected = {'some_key': "key"}
        to_parse = "some_key=key"
        result = await device_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_parse_scope_letters_line(self, device_service: DeviceService) -> None:
        expected:dict[str, Any] = {}
        to_parse = "gkljblsLHOouoiipUH:"
        result = await device_service._parse_scope_data(to_parse)
        assert result == expected

    async def test_clean_device_data(self, device_service: DeviceService, device_cancel_model: DeviceCancelModel) -> None:
        service = device_service
        service.request_model = device_cancel_model
        expected = f"http://{DOMAIN_NAME}/device/auth/cancel"
        await service.device_repo.create(
            client_id="test_client",
            device_code="urn:ietf:params:oauth:grant-type:device_code",
            user_code="user_code",
            verification_uri="some_uri",
            verification_uri_complete="complete_uri",
            expires_in=600,
            interval=5,
        )
        result = await service.clean_device_data("user_code")
        assert result == expected
        with pytest.raises(UserCodeNotFoundError):
            await service._validate_user_code(user_code="user_code")

    async def test_clean_device_data_client_not_exist(self, device_service: DeviceService, device_cancel_model: DeviceCancelModel) -> None:
        service = device_service
        service.request_model = device_cancel_model
        service.request_model.client_id = "bla1bla_io"
        with pytest.raises(ClientNotFoundError):
            await service.clean_device_data("ewtyuweyty")

    async def test_clean_device_data_device_not_exist(self, device_service: DeviceService, device_cancel_model: DeviceCancelModel) -> None:
        service = device_service
        service.request_model = device_cancel_model
        service.request_model.scope = "password=test_password&username=TestClient&user_code=blaBlabla"
        with pytest.raises(UserCodeNotFoundError):
            await service.clean_device_data("ewjwjefjewf")

    async def test_get_redirect_uri(self, device_service: DeviceService, device_user_code_model: DeviceUserCodeModel) -> None:
        service = device_service
        service.request_model = device_user_code_model
        expected_uri = f"http://{DOMAIN_NAME}/authorize/?client_id=test_client&" \
                       "response_type=urn:ietf:params:oauth:grant-type:device_code&" \
                       "redirect_uri=https://www.google.com/"
        await service.device_repo.create(
            client_id="test_client",
            device_code="urn:ietf:params:oauth:grant-type:device_code",
            user_code="GHJKTYUI",
            verification_uri="some_uri",
            verification_uri_complete="complete_uri",
            expires_in=600,
            interval=5,
        )
        await service.session.commit()
        result = await service.get_redirect_uri()
        assert result == expected_uri
        await service.device_repo.delete_by_user_code(user_code="GHJKTYUI")
        await service.session.commit()
        with pytest.raises(UserCodeNotFoundError):
            await service._validate_user_code(user_code="GHJKTYUI")

    async def test_get_redirect_uri_wrong_user_code(self, device_service: DeviceService, device_user_code_model: DeviceUserCodeModel) -> None:
        service = device_service
        service.request_model = device_user_code_model
        with pytest.raises(UserCodeNotFoundError):
            await service.get_redirect_uri()

    async def test_get_response(self, device_service: DeviceService, device_request_model: DeviceUserCodeModel) -> None:
        service = device_service
        service.request_model = device_request_model
        result = await service.get_response()
        if not result:
            raise AssertionError
        user_code = result["user_code"]

        assert isinstance(result, dict)
        # TODO: universify the acquisition of data for tests.
        # assert result["expires_in"] == 600
        code_exist = await service._validate_user_code(user_code=user_code)

        assert code_exist
        await service.device_repo.delete_by_user_code(user_code=user_code)
        with pytest.raises(UserCodeNotFoundError):
            await service._validate_user_code(user_code="user_code")

    async def test_get_response_wrong_client(self, device_service: DeviceService, device_request_model: DeviceRequestModel) -> None:
        service = device_service
        service.request_model = device_request_model
        service.request_model.client_id = "gnYth8OP"
        with pytest.raises(ClientNotFoundError):
            await service.get_response()
