import pytest

from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.errors import (
    WrongPasswordError,
    WrongPasswordFormatError,
)
from tests.test_unit.fixtures import TEST_VALIDATE_PASSWORD


class TestPasswordHash:
    def test_hash_password(self):
        password = PasswordHash.hash_password("some_password")
        assert type(password) == str

    def test_hash_password_wrong_format(self):
        with pytest.raises(WrongPasswordFormatError):
            password = PasswordHash.hash_password(2345)

    @pytest.mark.parametrize("test_input, expected", TEST_VALIDATE_PASSWORD[:3])
    def test_validate_password(self, test_input, expected):
        assert PasswordHash.validate_password(test_input, expected)

    @pytest.mark.parametrize("test_input, expected", TEST_VALIDATE_PASSWORD[3:])
    def test_validate_password_error(self, test_input, expected):
        with pytest.raises(WrongPasswordError):
            PasswordHash.validate_password(test_input, expected)
