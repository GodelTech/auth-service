from pydantic import BaseModel, Field


class RSAKeypair(BaseModel):
    private_key: bytes = Field(...)
    public_key: bytes = Field(...)

    n: int = Field(...)
    e: int = Field(...)
