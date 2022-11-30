import datetime

from sqlalchemy import Table, Date, String, Integer, Column, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from .base import BaseModel

user_roles = Table(
    "project_team",
    BaseModel.metadata,
    Column("role", Integer, ForeignKey("roles.id")),
    Column("user", Integer, ForeignKey("users.id")),
)

class UserLogin(BaseModel):
    __tablename__ = "user_logins"

    api_resources_id = Column("User", Integer,
                              ForeignKey('user.id'))
    login_provider = Column(String, primary_key=True, nullable=False, unique=True, )
    provider_key = Column(String, primary_key=True, nullable=False, unique=True, )

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
    access_failed_count = Column(Integer, default = 0, nullable=False)
    username = Column(String, nullable=False, unique=True)
    projects = relationship("Role", secondary = user_roles, back_populates = 'users')

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary = user_roles, back_populates = 'roles')

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class UserClaim(BaseModel):
    USER_CLAIM_TYPE = []
    __tablename__ = "user_claims"

    claim_type = type = Column(ChoiceType(USER_CLAIM_TYPE))
    claim_value = Column(String, nullable=False)
    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"