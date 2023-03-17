import bcrypt

from src.data_access.postgresql.errors import (
    WrongPasswordError,
    WrongPasswordFormatError,
)
from pydantic import SecretStr


class PasswordHash:
    @classmethod
    def hash_password(cls, password: str) -> str:
        if not isinstance(password, str):
            raise WrongPasswordFormatError("The password should be a string")
        bts = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(bts, salt)

        return str(hash_password).strip("b'")

    @classmethod
    def validate_password(
        cls, str_password: SecretStr, hash_password: str
    ) -> bool:
        str_password_bytes = str_password.get_secret_value().encode("utf-8")
        hash_password_bytes = bytes(hash_password.encode())
        is_valid = bcrypt.checkpw(str_password_bytes, hash_password_bytes)
        if not is_valid:
            raise WrongPasswordError(
                "You are trying to pass the wrong password to the scope"
            )
        return is_valid
