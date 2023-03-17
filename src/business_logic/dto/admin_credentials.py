from pydantic import BaseModel
from pydantic import SecretStr


class AdminCredentialsDTO(BaseModel):
    username: str
    password: SecretStr
