import pytest

from src.business_logic.services.jwt_token import JWTService


@pytest.mark.asyncio
class TestJWTService:

    async def test_encode_and_decode(self):
        service = JWTService()
        token = await service.encode_jwt(payload={"sub": 123, "name": "Danya"})
        assert token.count(".") == 2
        for tkn in (token, "Bearer " + token):
            decoded_dict = await service.decode_token(token=tkn)
            assert type(decoded_dict) == dict
            assert decoded_dict["sub"] == 123
            assert decoded_dict["name"] == "Danya"
