from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

user_group = Table(
    "users_groups",
    BaseModel.metadata,
    Column("groups", Integer, ForeignKey("groups.id")),
    Column("users", Integer, ForeignKey("users.id")),
)

permission_group = Table(
    "permissions_groups",
    BaseModel.metadata,
    Column("groups", Integer, ForeignKey("groups.id")),
    Column("permissions", Integer, ForeignKey("permissions.id")),
)


class Group(BaseModel):
    __tablename__ = "groups"

    name = Column(String, nullable=True, unique=True)
    parent_group = Column(int, ForeignKey("groups.name"))
    permissions = relationship(
        "Permissions", secondary="permissions_groups", back_populates="permissions"
    )
    def __str__(self):
        return self.name


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String, nullable=True, unique=True)
    groups = relationship(
        "Groups", secondary="permissions_groups", back_populates="groups"
    )
    def __str__(self):
        return self.namee   

    def __repr__(self) -> str:
        return self.name