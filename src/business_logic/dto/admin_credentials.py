from pydantic import BaseModel, SecretStr
from typing import Union

class AdminCredentialsDTO(BaseModel):
    username: str
    password: SecretStr
