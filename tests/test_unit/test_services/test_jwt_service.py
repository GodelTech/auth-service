import datetime

import mock
import pytest
from sqlalchemy import delete

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant


@pytest.mark.asyncio
class TestJWTService:

    async def test_encode_and_decode(self, connection):
        service = JWTService()
        token = await service.encode_jwt(secret="play", payload={"sub": 123, "name": "Danya"}, include_expire=False)
        assert token.count(".") == 2
        persistent_repo = PersistentGrantRepository(connection)
        await persistent_repo.create(
            client_id="double_test", data=token, user_id=2
        )
        for tkn in (token, "Bearer " + token):
            decoded_dict = await service.decode_token(secret="play", token=tkn)
            assert type(decoded_dict) == dict
            assert decoded_dict["sub"] == 123
            assert decoded_dict["name"] == "Danya"

        await persistent_repo.session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == "double_test")
            )
        await persistent_repo.session.commit()

    async def test_set_expire_time(self):
        service = JWTService()
        expire_days = 0
        expire_hours = 0
        expire_minutes = 0
        expire_seconds = 0

        with pytest.raises(ValueError):
            service.set_expire_time(
                expire_days, expire_hours, expire_minutes, expire_seconds
            )

        expire_days = 430
        expire_hours = 2340
        expire_minutes = -10
        expire_seconds = 2340

        with pytest.raises(ValueError):
            service.set_expire_time(
                expire_days, expire_hours, expire_minutes, expire_seconds
            )

        expire_days = 10
        expire_hours = 10
        expire_minutes = 10
        expire_seconds = 10

        def str_to_datetime(*args, **kwargs):
            return datetime.datetime.strptime(
                "2022-12-19 09:24:14", "%Y-%m-%d %H:%M:%S"
            )

        with mock.patch.object(
            JWTService, "get_datetime_now", new=str_to_datetime
        ):
            service.set_expire_time(
                expire_days, expire_hours, expire_minutes, expire_seconds
            )
            assert service.expire == datetime.datetime.strptime(
                "2022-12-29 19:34:24", "%Y-%m-%d %H:%M:%S"
            )
