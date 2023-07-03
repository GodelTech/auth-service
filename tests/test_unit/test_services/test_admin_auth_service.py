import mock
import pytest
from sqlalchemy import delete
from src.business_logic.services.admin_auth import AdminAuthService
from src.business_logic.dto.admin_credentials import AdminCredentialsDTO
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.errors.user import UserNotFoundError, UserNotInGroupError
from src.data_access.postgresql.errors import WrongPasswordError
from time import time, sleep
from jwt.exceptions import InvalidAudienceError, ExpiredSignatureError
from pydantic import SecretStr
from src.data_access.postgresql.repositories import UserRepository
from factories.commands import DataBasePopulation

async def new_check_user_group(*args, **kwargs):
    return True

@pytest.mark.asyncio
class TestAdminAuthService:
    async def test_authorize(
        self, admin_auth_service: AdminAuthService
    ) -> None:
        service = admin_auth_service
        credentials = AdminCredentialsDTO(
            username="PeterParker", password=SecretStr("the_beginner")
        )
        with mock.patch.object(
            UserRepository, "check_user_group", new=new_check_user_group
        ):
            result = await service.authorize(credentials=credentials)
            assert result

        with pytest.raises(UserNotInGroupError):
            await service.authorize(credentials=credentials)

        credentials = AdminCredentialsDTO(
            username="Vi", password=SecretStr("test_password")
        )
        with pytest.raises(UserNotFoundError):
            await service.authorize(credentials=credentials)

        credentials = AdminCredentialsDTO(
            username="TestClient", password=SecretStr("samurai")
        )
        with pytest.raises(WrongPasswordError):
            await service.authorize(credentials=credentials)

    async def test_authenticate(
        self, admin_auth_service: AdminAuthService
    ) -> None:
        service = admin_auth_service
        payload = {
            "aud": [
                "admin",
            ],
            "exp": int(time()) + 1000,
        }
        token = await JWTService().encode_jwt(payload)
        result = await service.authenticate(token=token)
        assert result is None

        payload = {
            "aud": [
                "not_admin",
            ],
            "exp": int(time()) + 1000,
        }
        token = await JWTService().encode_jwt(payload)
        result = await service.authenticate(token=token)
        assert result is not None

        payload = {
            "aud": [
                "admin",
            ],
            "exp": 0,
        }
        token = await JWTService().encode_jwt(payload)
        result = await service.authenticate(token=token)
        assert result is not None

    async def test_authorize_authenticate(
        self, admin_auth_service: AdminAuthService
    ) -> None:
        with mock.patch.object(
            UserRepository, "check_user_group", new=new_check_user_group
        ):
            service = admin_auth_service
            credentials = AdminCredentialsDTO(
                username="TestClient", password=SecretStr("test_password")
            )
            result = await service.authorize(credentials=credentials)
            assert type(result) is str
            result = await service.authenticate(token=result)
            assert result is None

            credentials = AdminCredentialsDTO(
                username="TestClient", password=SecretStr("test_password")
            )
            result = await service.authorize(credentials=credentials, exp_time=-10)
            result = await service.authenticate(token=result)
            assert result is not None