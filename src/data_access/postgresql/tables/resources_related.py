from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class ApiResource(BaseModel):
    __tablename__ = "api_resources"

    description = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    enabled = Column(Boolean, default=True, nullable=True)
    name = Column(String, nullable=False)
    api_scope = relationship(
        "ApiScope",
        back_populates="api_resources",
        lazy = 'immediate'
    )
    def __str__(self) -> str:  # pragma: no cover
        return f"Resource {self.id}: {self.name}"


class ApiSecret(BaseModel):
    __tablename__ = "api_secrets"
    api_resources_id = Column(
        Integer, ForeignKey("api_resources.id", ondelete="CASCADE")
    )
    api_resources = relationship(
        "ApiResource",
        backref="api_secret",
        lazy = 'joined'
    )
    description = Column(String, nullable=True)
    expiration = Column(DateTime, nullable=False)

    secret_type_id = Column(
        Integer,
        ForeignKey("api_secrets_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    secret_type = relationship(
        "ApiSecretType",
        lazy = 'joined'
    )

    value = Column(String, nullable=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Secret {self.id}: {self.description} {self.secret_type}"


class ApiSecretType(BaseModel):
    __tablename__ = "api_secrets_types"
    secret_type = Column(String, unique=True, nullable=False)

    def __str__(self) -> str:
        return f"{self.secret_type}"


class ApiClaim(BaseModel):
    __tablename__ = "api_claims"

    api_resources_id = Column(
        Integer, ForeignKey("api_resources.id", ondelete="CASCADE")
    )
    api_resources = relationship(
        "ApiResource",
        backref="api_claim",
    )

    claim_type_id = Column(
        Integer,
        ForeignKey("api_claim_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim_type = relationship(
        "ApiClaimType",
        backref="api_claim",
        foreign_keys="ApiClaim.claim_type_id",
    )
    claim_value = Column(String(30))

    def __str__(self) -> str:  # pragma: no cover
        return f"Claim {self.api_resources} - {self.id}"


class ApiClaimType(BaseModel):
    __tablename__ = "api_claim_types"
    claim_type = Column(String, unique=True, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"Claim Type: {self.claim_type}"


class ApiScope(BaseModel):
    __tablename__ = "api_scopes"

    api_resources_id = Column(
        Integer,
        ForeignKey("api_resources.id", ondelete="CASCADE"),
        nullable=False,
    )
    api_resources = relationship(
        "ApiResource",
        back_populates="api_scope",
        lazy = 'noload'
    )
    api_scope_claims = relationship(
        "ApiScopeClaim",
        back_populates="api_scopes",
        lazy = 'immediate',
    )
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    emphasize = Column(Boolean, default=False, nullable=True)
    required = Column(Boolean, default=False, nullable=True)
    show_in_discovery_document = Column(Boolean, default=False, nullable=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Scope {self.display_name} ({self.name})"


class ApiScopeClaim(BaseModel):
    __tablename__ = "api_scope_claims"

    api_scopes_id = Column(
        Integer, ForeignKey("api_scopes.id", ondelete="CASCADE")
    )
    api_scopes = relationship(
        "ApiScope",
        back_populates="api_scope_claims",
        lazy = 'noload',
    )

    scope_claim_type_id = Column(
        Integer,
        ForeignKey("api_scope_claim_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    scope_claim_type = relationship(
        "ApiScopeClaimType",
        back_populates="scope_claim",
        lazy = 'immediate'
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.scope_claim_type}"


class ApiScopeClaimType(BaseModel):
    __tablename__ = "api_scope_claim_types"
    scope_claim_type = Column(String, unique=True, nullable=False)
    scope_claim = relationship(
        "ApiScopeClaim",
        back_populates="scope_claim_type",
        lazy = 'immediate'
    )
    def __str__(self) -> str:  # pragma: no cover
        return self.scope_claim_type

    def __repr__(self) -> str:  # pragma: no cover
        return self.scope_claim_type


class ClientScope(BaseModel):
    __tablename__ = "client_scopes"

    client_id = Column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE")
    )
    client = relationship(
        "Client",
        back_populates="scopes",
        lazy = 'noload'
    )

    resource_id = Column(
        Integer, ForeignKey("api_resources.id", ondelete="CASCADE")
    )
    resource = relationship(
        "ApiResource",
        lazy = 'immediate'
    )

    scope_id = Column(
        Integer, ForeignKey("api_scopes.id", ondelete="CASCADE")
    )
    scope = relationship(
        "ApiScope",
        lazy = 'immediate'
    )

    claim_id = Column(
        Integer,
        ForeignKey("api_scope_claim_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim = relationship(
        "ApiScopeClaimType",
        lazy = 'immediate'
    )

    def __repr__(self) -> str:
        self.__str__()
    
    def __str__(self) -> str:
        return f'{self.resource.name}.{self.scope.name}.{self.claim.scope_claim_type}'
    