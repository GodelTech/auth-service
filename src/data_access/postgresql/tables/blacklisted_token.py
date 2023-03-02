from .base import Base, BaseModel

from sqlalchemy import Integer, String, Column

class BlacklistedToken(BaseModel):
    __tablename__ = "blacklisted_tokens"
    
    token = Column(String(1024), nullable=False)
    expiration = Column(Integer, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.token}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.token}"