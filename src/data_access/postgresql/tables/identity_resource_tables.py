from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text

from .base import Base


class IdentityClaims(Base):
    __tablename__ = "identity_claims"

    id = Column(Integer, primary_key=True)
    identity_resource_id = Column(Integer, ForeignKey("identity_resources.id"))
    type = Column(Text)

    def __str__(self) -> str:
        return self.__tablename__


class IdentityResourses(Base):
    __tablename__ = "identity_resources"

    id = Column(Integer, primary_key=True)
    description = Column(Text)
    display_name = Column(String, nullable=False)
    emphasize = Column(Boolean) # this record needs to be emphasized or not?
    enabled = Column(Boolean, nullable=False)
    name = Column(String)
    required = Column(Boolean)
    show_in_discovery_document = Column(Boolean)

    def __str__(self) -> str:
        return self.__tablename__