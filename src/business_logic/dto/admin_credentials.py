from pydantic import BaseModel


class AdminCredentialsDTO(BaseModel):
    username: str
    password: str
