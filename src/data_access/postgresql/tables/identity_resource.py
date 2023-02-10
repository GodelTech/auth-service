from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class IdentityClaim(BaseModel):
    __tablename__ = "identity_claims"

    identity_resource_id = Column(Integer, ForeignKey("identity_resources.id", ondelete='CASCADE'))
    identity_resource = relationship("IdentityResource", back_populates = "identity_claim", foreign_keys = "IdentityClaim.identity_resource_id")
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

    identity_claim = relationship("IdentityClaim", back_populates = "identity_resource", foreign_keys = "IdentityClaim.identity_resource_id")
    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.name}"
