import datetime

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=datetime.datetime.now
    )


class Note(BaseModel):
    __tablename__ = "notes"

    title = Column(String, nullable=False, index=True)
    content = Column(String, index=True)
    user_id = Column(
        Integer,
    )  # ForeignKey("xyz"))
    # user = relationship("xyz")


class UserInfo(Base):
    __tablename__ = "users_info"

    id = Column(Integer, primary_key=True)
    sub = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    middle_name = Column(String, nullable=False)
    given_name = Column(String, nullable=False)
    family_name = Column(String, nullable=False)
    nickname = Column(String, nullable=False, unique=True)
    preferred_username = Column(String, nullable=False)
    profile = Column(String, nullable=False)
    picture = Column(String, nullable=False)
    website = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    email_verified = Column(Boolean, nullable=False)
    gender = Column(String, nullable=False)
    birthdate = Column(String, nullable=False)
    zoneinfo = Column(String, nullable=False)
    locale = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    phone_number_verified = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    updated_at = Column(Integer, nullable=False)  # TODO change to timestamp
