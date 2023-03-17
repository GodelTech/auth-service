from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base, BaseModel


class IdentityClaim(BaseModel):
    __tablename__ = "identity_claims"

    identity_resource_id = Column(
        Integer, ForeignKey("identity_resources.id", ondelete="CASCADE")
    )
    identity_resource = relationship(
        "IdentityResource",
        back_populates="identity_claim",
        foreign_keys="IdentityClaim.identity_resource_id",
    )
    type = Column(String)

    def __str__(self) -> str:  # pragma: no cover
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

    identity_claim = relationship(
        "IdentityClaim",
        back_populates="identity_resource",
        foreign_keys="IdentityClaim.identity_resource_id",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.__tablename__}: {self.name}"


class IdentityProviderMapped(BaseModel):
    __tablename__ = "identity_providers_mapped"

    identity_provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    identity_provider = relationship(
        "IdentityProvider",
        back_populates="identity_providers_mapped",
        foreign_keys="IdentityProviderMapped.identity_provider_id",
        lazy="joined",
    )

    provider_client_id = Column(String, nullable=False)
    provider_client_secret = Column(String, nullable=False)

    enabled = Column(Boolean, default=True, nullable=False)

    def __str__(self) -> str:
        if self.enabled:
            return f"id: {self.id} | Client_id : {self.provider_client_id} | Status : ON"
        else:
            return f"id: {self.id} | Client_id : {self.provider_client_id} | Status : OFF"


class IdentityProvider(BaseModel):
    __tablename__ = "identity_providers"

    name = Column(String, nullable=False, unique=True)
    auth_endpoint_link = Column(String, nullable=False)
    token_endpoint_link = Column(String, nullable=False)
    userinfo_link = Column(String, nullable=False)
    internal_redirect_uri = Column(String, nullable=False)
    provider_icon = Column(String(100), nullable=False)

    identity_providers_mapped = relationship(
        "IdentityProviderMapped",
        back_populates="identity_provider",
        foreign_keys="IdentityProviderMapped.identity_provider_id",
    )
    users = relationship(
        "User",
        back_populates="identity_provider",
        foreign_keys="User.identity_provider_id",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name}\t|\t{self.internal_redirect_uri}"


class IdentityProviderState(BaseModel):
    __tablename__ = "identity_provider_states"

    state = Column(String, nullable=False, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.state}"
