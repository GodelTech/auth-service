import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from src.data_access.postgresql.tables.group import users_groups, permissions_roles
from .base import Base, BaseModel



users_roles = Table(
    "users_roles",
    BaseModel.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class UserLogin(BaseModel):
    __tablename__ = "user_logins"

    user_id = Column("User", Integer, ForeignKey("users.id", ondelete='CASCADE'))
    login_provider = Column(
        String,
        primary_key=True,
        nullable=False,
        unique=True,
    )
    provider_key = Column(
        String,
        primary_key=True,
        nullable=False,
        unique=True,
    )

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.client_name}"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, nullable=True, unique=True)
    email_confirmed = Column(Boolean, default=False, nullable=True)
    password_hash = Column(String, nullable=False)
    security_stamp = Column(String, nullable=True)
    phone_number = Column(String, nullable=False, unique=True)
    phone_number_confirmed = Column(Boolean, default=False, nullable=True)
    two_factors_enabled = Column(Boolean, default=True, nullable=True)
    lockout_end_date_utc = Column(Date, nullable=True)
    lockout_enabled = Column(Boolean, default=True, nullable=True)
    access_failed_count = Column(Integer, default=0, nullable=False)
    username = Column(String, nullable=False, unique=True)
    roles = relationship(
        "Role", secondary="users_roles", back_populates="users"
    )
    groups = relationship(
        "Group", secondary="users_groups", back_populates="users"
    )
    def __repr__(self):
        return  f"{self.id} id - {self.username}"
    def __str__(self):
        return f"{self.id} id - {self.username}"
    #claims = relationship("UserClaim", back_populates="user", cascade="all, delete-orphan")

class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, nullable=False, unique=True)
    users = relationship(
        "User", secondary= users_roles, back_populates="roles"
    )
    permissions = relationship(
        "Permission", secondary= permissions_roles, back_populates="roles"
    )

    def __str__(self):
        return f"Role {self.name} - {self.id}"


class UserClaim(BaseModel):
   
    __tablename__ = "user_claims"
   # user_id = Column("User", Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
# user = relationship("User", back_populates="claims")
    claim_type_id = Column(Integer, ForeignKey("USER_CLAIM_TYPE.id", ondelete='CASCADE'), nullable=False)
    claim_type = relationship("ChoiceUserClaimType", back_populates="userclaim")
    claim_value = Column(String, nullable=False)

    def __str__(self):
        return f"{self.claim_type}: {self.claim_value}"
