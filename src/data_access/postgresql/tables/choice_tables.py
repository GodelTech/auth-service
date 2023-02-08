

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from .base import BaseModel


ACCESS_TOKEN_TYPES = ["jwt", "reference",]
PROTOCOL_TYPES = ["open_id_connect", "open_id_connect2"]
REFRESH_TOKEN_EXPIRATION = ["absolute", "sliding"]
REFRESH_TOKEN_USAGE = ["one_time_only", "reuse"]

# Client choices
class ChoiceAccessTokenType(BaseModel):
    __tablename__ = "access_token_types"

    type = Column(String, unique=True)
    client = relationship("Client", back_populates="access_token_type", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"Token type: {self.type}"
    
# class ChoiceProtokolType(BaseModel):
#     __tablename__ = "protocol_types"

#     type = Column(String, unique=True)
#     client = relationship("Client", back_populates="protocol_type", cascade="all, delete-orphan")
#     def __str__(self) -> str:
#         return f"{self.type}"
    
#     def __repr__(self) -> str:
#         return f"Protokol type: {self.type}"
    
# class ChoiceRefreshTokenExpirationType(BaseModel):
#     __tablename__ = "refresh_token_types"

#     type = Column(String, unique=True)
#     client = relationship("Client", back_populates="refresh_token_expiration", cascade="all, delete-orphan")
#     def __str__(self) -> str:
#         return f"{self.type}"
    
#     def __repr__(self) -> str:
#         return f"{self.type}"

# class ChoiceRefreshTokenUsageType(BaseModel):
#     __tablename__ = "refresh_token_usage_types"

#     type = Column(String, unique =True)
#     client = relationship("Client", back_populates="refresh_token_usage", cascade="all, delete-orphan")
#     def __str__(self) -> str:
#         return f"{self.type}"
    
#     def __repr__(self) -> str:
#         return f"{self.type}"
    

# UserClaims


# class ChoiceUserClaimType(BaseModel):
#     
    # __tablename__ = "user_claim_types"

    # type = Column(String, unique =True)
    # userclaims = relationship("UserClaim",  cascade="all, delete-orphan", back_populates="claim_type",)
    
    # def __str__(self) -> str:
    #     return f"{self.type}"
    
    # def __repr__(self) -> str:
    #     return f"{self.type}"