import pytest
import mock
import datetime
from src.business_logic.services.jwt_token import JWTService


@pytest.mark.asyncio
class TestJWTServiece():

    @classmethod
    def setup_class(cls):
        cls.jwt = JWTService()
        cls.jwt.set_expire_time(expire_days=1)

    def test_encode_and_decode(self):
        token = self.jwt.encode_jwt(payload={"sub": 123, "name": "Danya"})
        assert token.count('.') == 2

        for tkn in (token, "Bearer " + token):
            decoded_dict = self.jwt.decode_token(tkn)
            assert type(decoded_dict) == dict
            assert decoded_dict["sub"] == 123
            assert decoded_dict["name"] == "Danya"
    
    def test_set_expire_time(self):
        
        expire_days = 0
        expire_hours = 0
        expire_minutes = 0
        expire_seconds = 0

        with pytest.raises(ValueError):
            self.jwt.set_expire_time(expire_days, expire_hours, expire_minutes, expire_seconds)


        expire_days = 430
        expire_hours = 2340
        expire_minutes = -10
        expire_seconds = 2340

        with pytest.raises(ValueError):
            self.jwt.set_expire_time(expire_days, expire_hours, expire_minutes, expire_seconds)

        expire_days = 10
        expire_hours = 10
        expire_minutes = 10
        expire_seconds = 10


        def str_to_datetime(*args, **kwargs):
            return datetime.datetime.strptime("2022-12-19 09:24:14", '%Y-%m-%d %H:%M:%S')

        with mock.patch.object(JWTService, "get_datetime_now", new=str_to_datetime):
            self.jwt.set_expire_time(expire_days, expire_hours, expire_minutes, expire_seconds)
            assert self.jwt.expire == datetime.datetime.strptime("2022-12-29 19:34:24", '%Y-%m-%d %H:%M:%S')
