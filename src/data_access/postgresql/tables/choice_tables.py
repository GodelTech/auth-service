

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from .base import BaseModel

from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BaseModel2(Base):
    __abstract__ = True

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=datetime.datetime.now
    )

ACCESS_TOKEN_TYPES = ["jwt", "reference",]
PROTOCOL_TYPES = ["open_id_connect", "open_id_connect2"]
REFRESH_TOKEN_EXPIRATION = ["absolute", "sliding"]
REFRESH_TOKEN_USAGE = ["one_time_only", "reuse"]

# Client choices
class ChoiseAccessTokenType(BaseModel):
    __tablename__ = "ACCESS_TOKEN_TYPES"

    type = Column(String, unique=True)
    client = relationship("Client", back_populates="access_token_type")

    def __str__(self) -> str:
        return f"{self.__name__}"
    
    def __repr__(self) -> str:
        return f"Token type: {self.__name__}"
    
class ChoiseProtokolType(BaseModel):
    __tablename__ = "PROTOCOL_TYPES"

    type = Column(String, unique=True)
    client = relationship("Client", back_populates="protocol_type")
    def __str__(self) -> str:
        return f"{self.__name__}"
    
    def __repr__(self) -> str:
        return f"Protokol type: {self.__name__}"
    
class ChoiseRefreshTokenExpirationType(BaseModel):
    __tablename__ = "REFRESH_TOKEN_EXPIRATION"

    type = Column(String, unique=True)
    client = relationship("Client", back_populates="refresh_token_expiration")
    def __str__(self) -> str:
        return f"{self.__name__}"
    
    def __repr__(self) -> str:
        return f"Expiration type: {self.__name__}"

class ChoiseRefreshTokenUsageType(BaseModel):
    __tablename__ = "REFRESH_TOKEN_USAGE"

    type = Column(String, unique =True)
    client = relationship("Client", back_populates="refresh_token_usage")
    def __str__(self) -> str:
        return f"{self.__name__}"
    
    def __repr__(self) -> str:
        return f"Usage type: {self.__name__}"
    

# UserClaims


class ChoiceUserClaimType(BaseModel):
    __tablename__ = "USER_CLAIM_TYPE"

    type = Column(String, unique =True)
    userclaim = relationship("UserClaim", back_populates="claim_type", cascade="all, delete-orphan", lazy='joined')
    
    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"Usage type: {self.type}"