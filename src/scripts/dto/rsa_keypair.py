from pydantic import Field
from pydantic import BaseModel


class RSAKeypair(BaseModel):
    private_key: bytes = Field(...)
    public_key: bytes = Field(...)

    n: int = Field(...)
    e: int = Field(...)
