import bcrypt


class PasswordHash:

    @classmethod
    def hash_password(cls, password: str) -> bytes:
        bts = password.encode('utf-8')
        salt = bcrypt.gensalt()

        return bcrypt.hashpw(bts, salt)

    @classmethod
    def validate_password(cls, str_password: str, hash_password: bytes) -> bool:
        str_password_bytes = str_password.encode('utf-8')

        return bcrypt.checkpw(str_password_bytes, hash_password)
