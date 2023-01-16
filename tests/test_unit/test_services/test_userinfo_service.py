import datetime

import mock
import pytest

from src.business_logic.dependencies import get_repository
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.userinfo import UserInfoServies
from src.data_access.postgresql.repositories.user import UserRepository
from src.business_logic.services.tokens import TokenService

class RequestMock:
    authorization = 0


@pytest.mark.asyncio
class TestUserInfoServiece:
    @classmethod
    def setup_class(cls):
        request = RequestMock()
        request.authorization = 1
        cls.uis = UserInfoServies()
        cls.uis.jwt.set_expire_time(expire_hours=1)
        cls.uis.request = request
        cls.uis.user_repo = get_repository(UserRepository)
        cls.uis.user_repo = cls.uis.user_repo()

    async def test_get_user_info_and_get_user_info_jwt(self):
        def new_decode_token(*args, **kwargs):
            return {"sub": 1, "expire": str(self.uis.jwt.expire)}

        async def new_get_user_info_dict(*args, **kwargs):
            return {
                "name": "Danya",
                "given_name": "Ibragim",
                "family_name": "Krats",
                "middle_name": "-el-",
                "nickname": "Nagibator2000",
            }
        
        async def new_check_authorisation_token(*args, **kwargs):
            return True

        with mock.patch.object(
            TokenService, "check_authorisation_token", new=new_check_authorisation_token
        ):
            with mock.patch.object(
                UserRepository, "get_claims", new=new_get_user_info_dict
            ):
                with mock.patch.object(
                    JWTService, "decode_token", new=new_decode_token
                ):
                    expected_part_one = {"sub": str(new_decode_token()["sub"])}
                    expected_part_two = await new_get_user_info_dict()
                    expected = expected_part_one | expected_part_two
                    result = await self.uis.get_user_info()
                    result_jwt = await self.uis.get_user_info_jwt()

                    assert expected == result
                    assert (
                        self.uis.jwt.encode_jwt(expected, include_expire=False)
                        == result_jwt
                    )
