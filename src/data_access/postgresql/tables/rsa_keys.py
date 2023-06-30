from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text
)

from .base import BaseModel

class RSA_keys(BaseModel):
    __tablename__ = "rsa_keys"

    private_key = Column(LargeBinary)
    public_key = Column(LargeBinary)
    n = Column(Numeric)
    e = Column(Integer)
    expiration_encode = Column(Integer, default=0)
    expiration_decode = Column(Integer, default=0)