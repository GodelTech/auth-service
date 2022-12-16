import pytest
from src.business_logic.services.jwt_token import JWTService


@pytest.mark.asyncio
class TestJWTServiece():

    @classmethod
    def setup_class(cls):
        cls.jwt = JWTService()

    def test_encode_and_decode(self):
        token = self.jwt.encode_jwt(payload={"sub": 123, "name": "Danya"})
        assert token.count('.') == 2

        for tkn in (token, "Bearer " + token):
            decoded_dict = self.jwt.decode_token(tkn)
            assert type(decoded_dict) == dict
            assert decoded_dict["sub"] == 123
            assert decoded_dict["name"] == "Danya"
