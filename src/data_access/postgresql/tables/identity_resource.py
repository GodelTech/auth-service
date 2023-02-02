from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy_utils import ChoiceType

from .base import BaseModel


class IdentityClaim(BaseModel):
    __tablename__ = "identity_claims"

    identity_resource_id = Column(Integer, ForeignKey("identity_resources.id", ondelete='CASCADE'))
    type = Column(String)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.id}"


class IdentityResource(BaseModel):
    __tablename__ = "identity_resources"

    description = Column(String(512), nullable=True)
    display_name = Column(String(32), nullable=False)
    emphasize = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    name = Column(String(32), nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    show_in_discovery_document = Column(Boolean, default=False, nullable=False)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.name}"
