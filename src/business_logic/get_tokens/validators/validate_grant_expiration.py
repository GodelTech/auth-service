import time
from src.business_logic.get_tokens.errors import InvalidGrantError


class ValidateGrantExpired:
    def __call__(self, grant_expiration: int) -> None:
        if time.time() > grant_expiration:
            raise InvalidGrantError
