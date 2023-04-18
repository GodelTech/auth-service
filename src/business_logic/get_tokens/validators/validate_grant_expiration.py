from src.business_logic.get_tokens.errors import InvalidGrantError


class ValidateGrantExpired:
    def __call__(self, grant_created_datetime: str, grant_expiration: int) -> None:
        pass
