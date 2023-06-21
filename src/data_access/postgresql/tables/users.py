import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from src.data_access.postgresql.tables.group import (
    permissions_roles,
    users_groups,
)

from .base import Base, BaseModel


users_roles = Table(
    "users_roles",
    BaseModel.metadata,
    Column(
        "role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
)


class UserLogin(BaseModel):
    __tablename__ = "user_logins"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # user = relationship("User", backref = "login",)
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

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.login_provider}: {self.provider_key}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.login_provider}: {self.provider_key}"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, nullable=True, unique=True)
    email_confirmed = Column(Boolean, default=False, nullable=True)

    password_hash_id = Column(
        Integer,
        ForeignKey("user_passwords.id", ondelete="SET NULL"),
        nullable=True,
    )
    password_hash = relationship(
        "UserPassword",
        back_populates="user",
        foreign_keys="User.password_hash_id",
        lazy="joined",
    )

    identity_provider_id = Column(
        Integer,
        ForeignKey("identity_providers.id", ondelete="SET NULL"),
        nullable=True,
    )
    identity_provider = relationship(
        "IdentityProvider",
        back_populates="users",
        foreign_keys="User.identity_provider_id",
        lazy="joined",
    )

    security_stamp = Column(String, nullable=True)
    phone_number = Column(String, nullable=True, unique=True)
    phone_number_confirmed = Column(Boolean, default=False, nullable=False)
    two_factors_enabled = Column(Boolean, default=False, nullable=False)
    lockout_end_date_utc = Column(Date, nullable=True)
    lockout_enabled = Column(Boolean, default=False, nullable=True)
    access_failed_count = Column(Integer, default=0, nullable=False)
    username = Column(String, nullable=False, unique=True)
    roles = relationship(
        "Role", secondary="users_roles", back_populates="users"
    )
    groups = relationship(
        "Group", 
        secondary="users_groups", 
        back_populates="users",
        lazy = "immediate"
    )
    claims = relationship(
        "UserClaim", 
        back_populates="user", 
        foreign_keys="UserClaim.user_id", 
      #  lazy = "subquery"
    )
    grants = relationship(
        "PersistentGrant",
        back_populates="user",
        foreign_keys="PersistentGrant.user_id",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"id {self.id}\t{self.username}"


class UserPassword(BaseModel):
    __tablename__ = "user_passwords"
    value = Column(String, nullable=False)
    user = relationship(
        "User",
        back_populates="password_hash",
        foreign_keys="User.password_hash_id",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.value}"


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary=users_roles, back_populates="roles")
    permissions = relationship(
        "Permission", secondary=permissions_roles, back_populates="roles"
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.id}: {self.name}"


class UserClaim(BaseModel):
    __tablename__ = "user_claims"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="claims")

    claim_type_id = Column(
        Integer,
        ForeignKey("user_claim_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim_type = relationship("UserClaimType", backref="claim", lazy = "subquery")
    claim_value = Column(String, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.claim_type_id}: {self.claim_value}"


class UserClaimType(Base):
    __tablename__ = "user_claim_types"
    id = Column(Integer, primary_key=True)
    type_of_claim = Column(String, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type_of_claim}"
