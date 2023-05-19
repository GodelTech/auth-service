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

API_SECRET_TYPE = ["sha256", "sha512"]
API_CLAIM_TYPE = ["string", "string2"]
API_SCOPE_CLAIM_TYPE = [
    "name",
    "family_name",
    "middle_name",
    "nickname",
    "preferred_username",
    "profile_picture",
    "website",
    "gender",
    "birthdate",
    "zone_info",
    "locale",
    "updated_at",
]


class ApiResource(BaseModel):
    __tablename__ = "api_resources"

    description = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    enabled = Column(Boolean, default=True, nullable=True)
    name = Column(String, nullable=False)
    api_scope = relationship(
        "ApiScope",
        back_populates="api_resources",
        foreign_keys="ApiScope.api_resources_id",
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
        foreign_keys="ApiSecret.api_resources_id",
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
        foreign_keys="ApiSecret.secret_type_id",
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
        foreign_keys="ApiClaim.api_resources_id",
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
        foreign_keys="ApiScope.api_resources_id",
    )
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    emphasize = Column(Boolean, default=False, nullable=True)
    required = Column(Boolean, default=False, nullable=True)
    show_in_discovery_document = Column(Boolean, default=False, nullable=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Scope {self.id}: {self.name}"


class ApiScopeClaim(BaseModel):
    __tablename__ = "api_scope_claims"

    api_scopes_id = Column(
        Integer, ForeignKey("api_scopes.id", ondelete="CASCADE")
    )
    api_scopes = relationship(
        "ApiScope",
        backref="api_scope_claim",
        foreign_keys="ApiScopeClaim.api_scopes_id",
    )

    scope_claim_type_id = Column(
        Integer,
        ForeignKey("api_scope_claim_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    scope_claim_type = relationship(
        "ApiScopeClaimType",
        foreign_keys="ApiScopeClaim.scope_claim_type_id",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"Scope-Claim {self.api_scopes}: {self.scope_claim_type}"


class ApiScopeClaimType(BaseModel):
    __tablename__ = "api_scope_claim_types"
    scope_claim_type = Column(String, unique=True, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"Scope-Claim Type: {self.scope_claim_type}"
