import mock
import pytest
from sqlalchemy import delete

from src.business_logic.services.userinfo import UserInfoServices
from src.presentation.api.models.userinfo import ResponseUserInfoModel
from sqlalchemy.ext.asyncio.engine import AsyncEngine


class RequestMock:
    authorization = 0


@pytest.mark.asyncio
class TestUserInfoService:

    async def test_get_user_info_and_get_user_info_jwt(self, user_info_service: UserInfoServices, connection:AsyncEngine) -> None:
        service = user_info_service
        data_to_code = {
                "scope":"openid profile",
                "sub": 1,
            }

        token = await service.jwt.encode_jwt(payload=data_to_code)
        service.authorization = token

        expected_part_one = {"sub": "1", }
        expected_part_two = {
            "name": "Daniil",
            "given_name": "Ibragim",
            "family_name": "Krats",
            "middle_name": "-el-",
            "nickname": "Nagibator2000",
        }
        expected = expected_part_one | expected_part_two
        result = await service.get_user_info()
        expected_jwt = token
        result_jwt = await service.get_user_info_jwt()

        assert expected["name"] == result["name"]
        assert expected["given_name"] == result["given_name"]
        assert expected["nickname"] == result["nickname"]

        assert expected_jwt[:10] == result_jwt[:10]

        