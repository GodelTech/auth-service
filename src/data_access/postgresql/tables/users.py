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


USER_CLAIM_TYPE = [
        "name", 
        "given_name",
        "family_name",
        "middle_name",
        "nickname", 
        "preferred_username", 
        "profile",
        "picture",
        "website",
        "email", 
        "email_verified",
        "gender", 
        "birthdate",
        "zoneinfo",
        "locale", 
        "phone_number", 
        "phone_number_verified",
        "address", 
        "updated_at", 
    ]

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
    claims = relationship("UserClaim", backref = "user", foreign_keys="UserClaim.user_id")

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


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

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    claim_type = Column(String, ForeignKey("user_claim_types.type", ondelete='CASCADE'), nullable=False)
    claim_value = Column(String, nullable=False)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"

class UserClaimTypes(Base):
   
    __tablename__ = "user_claim_types"

    type = Column(String, primary_key=True)
    claim = relationship("UserClaim", backref = "type",) #foreign_keys="UserClaim.claim_type_id") #foreign_keys="UserClaim.user_id")
    

    def __str__(self):
        return f"{self.type}"