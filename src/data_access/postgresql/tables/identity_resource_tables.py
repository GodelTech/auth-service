from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy_utils import ChoiceType

from .base import BaseModel


class IdentityClaims(BaseModel):
    __tablename__ = "identity_claims"

    id = Column(Integer, primary_key=True)
    identity_resource_id = Column(Integer, ForeignKey("identity_resources.id"))
    type = Column(String)

    def __str__(self) -> str:
        return self.__tablename__


class IdentityResourses(BaseModel):
    __tablename__ = "identity_resources"

    id = Column(Integer, primary_key=True)
    description = Column(String(512), nullable=True)
    display_name = Column(String(32), nullable=False)
    emphasize = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    name = Column(String(32), nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    show_in_discovery_document = Column(Boolean, default=False, nullable=False)

    def __str__(self) -> str:
        return self.__tablename__