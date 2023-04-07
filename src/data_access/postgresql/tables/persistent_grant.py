from datetime import datetime, timedelta

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

# from src.data_access.postgresql.tables.client import Client


LIFESPAN_OF_TOKEN = 999

TYPES_OF_GRANTS = ["authorization_code", "refresh_token"]


class PersistentGrant(BaseModel):
    __tablename__ = "persistent_grants"

    key = Column(String(512), unique=True, nullable=False)
    client_id = Column(
        Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    client = relationship(
        "Client",
        back_populates="grants",
        foreign_keys="PersistentGrant.client_id",
        lazy="joined",
    )
    grant_data = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship(
        "User", back_populates="grants", foreign_keys="PersistentGrant.user_id"
    )

    persistent_grant_type_id = Column(
        Integer,
        ForeignKey("persistent_grant_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    persistent_grant_type = relationship(
        "PersistentGrantType",
        backref="grants",
        foreign_keys="PersistentGrant.persistent_grant_type_id",
        lazy="joined",
    )

    code_challenge = Column(String, nullable=True)

    def __str__(self) -> str:  # pragma: no cover
        return f":{self.expiration}"


class PersistentGrantType(Base):
    __tablename__ = "persistent_grant_types"
    id = Column(Integer, primary_key=True)
    type_of_grant = Column(String, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type_of_grant}"
