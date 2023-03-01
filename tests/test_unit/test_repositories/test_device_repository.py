from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncEngine
import pytest

from src.data_access.postgresql.errors import (
    DeviceCodeNotFoundError,
    UserCodeNotFoundError,
)
from src.data_access.postgresql.repositories import DeviceRepository
from typing import no_type_check

TEST_DEVICE_DATA = {
    "client_id": "test_client",
    "device_code": "device_code",
    "user_code": "user_code",
    "verification_uri": "verification_uri",
    "verification_uri_complete": "verification_uri_complete",
    "expires_in": 600,
    "interval": 5,
}


@pytest.mark.asyncio
class TestClientRepository:
    async def test_create_delete_by_device_code(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        await device_repo.create(
            client_id="test_client", 
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
            expires_in=600,
            interval = 5
            )

        created = await device_repo.validate_device_code(device_code="device_code")
        assert created is True

        await device_repo.delete_by_device_code(device_code="device_code")
        with pytest.raises(DeviceCodeNotFoundError):
            await device_repo.validate_device_code(device_code="device_code")
    
    @no_type_check
    async def test_create_not_full_data(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        with pytest.raises(TypeError):
            await device_repo.create(
                device_code="device_code",
                user_code="user_code",
                verification_uri="verification_uri",
            )

    async def test_delete_by_user_code(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        await device_repo.create(
            client_id="test_client",
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
        )
        created = await device_repo.validate_device_code(device_code="device_code")
        assert created is True
        await device_repo.delete_by_user_code(user_code="user_code")

        with pytest.raises(UserCodeNotFoundError):
            await device_repo.validate_user_code(user_code="user_code")

    async def test_delete_by_user_code_not_exist(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        with pytest.raises(UserCodeNotFoundError):
            await device_repo.delete_by_user_code(user_code="fhjhYTU3")

    async def test_delete_by_device_code_not_exist(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        with pytest.raises(DeviceCodeNotFoundError):
            await device_repo.delete_by_device_code(device_code="fhjhYTU3")

    async def test_validate_user_code(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        await device_repo.create(
            client_id="test_client", 
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
            expires_in=600,
            interval = 5
            )

        validated = await device_repo.validate_user_code(user_code="user_code")
        assert validated is True

        await device_repo.delete_by_user_code(user_code="user_code")

        with pytest.raises(UserCodeNotFoundError):
            await device_repo.validate_user_code(user_code="user_code")

    async def test_validate_device_code(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        await device_repo.create(
            client_id="test_client", 
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
            expires_in=600,
            interval = 5
            )

        validated = await device_repo.validate_device_code(device_code="device_code")
        assert validated is True

        await device_repo.delete_by_device_code(device_code="device_code")

        with pytest.raises(DeviceCodeNotFoundError):
            await device_repo.validate_device_code(device_code="device_code")

    async def test_get_device_by_user_code(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)
        await device_repo.create(
            client_id="test_client", 
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
            expires_in=600,
            interval = 5
        )

        device = await device_repo.get_device_by_user_code(user_code="user_code")
        assert device.client.client_id == "test_client"
        assert device.device_code == "device_code"

        await device_repo.delete_by_user_code(user_code="user_code")

        with pytest.raises(UserCodeNotFoundError):
            await device_repo.get_device_by_user_code(user_code="user_code")

    async def test_get_expiration_time(self, engine: AsyncEngine) -> None:
        device_repo = DeviceRepository(engine=engine)

        await device_repo.create(
            client_id="test_client", 
            device_code="device_code",
            user_code="user_code",
            verification_uri="verification_uri",
            verification_uri_complete="verification_uri_complete",
            expires_in=600,
            interval = 5
            )

        now = datetime.utcnow()
        now_time = datetime.timestamp(now)
        expiration_time = await device_repo.get_expiration_time(device_code="device_code")
        assert expiration_time > now_time

        await device_repo.delete_by_user_code(user_code="user_code")
        with pytest.raises(UserCodeNotFoundError):
            await device_repo.get_device_by_user_code(user_code="user_code")
