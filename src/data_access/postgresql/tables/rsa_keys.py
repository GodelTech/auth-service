from sqlalchemy import (
    Column,
    Integer,
    LargeBinary
)

from .base import BaseModel

class RSA_keys(BaseModel):
    __tablename__ = "rsa_keys"

    private_key = Column(LargeBinary)
    public_key = Column(LargeBinary)
    n = Column(Integer)
    e = Column(Integer)