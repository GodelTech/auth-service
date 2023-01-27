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

users_groups = Table(
    "users_groups",
    BaseModel.metadata,
    Column("group_id",  ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

permissions_groups = Table(
    "permissions_groups",
    BaseModel.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)

permissions_roles = Table(
    "permissions_roles",
    BaseModel.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Group(BaseModel):
    __tablename__ = "groups"

    name = Column(String, unique=False)
    parent_group = Column(Integer, ForeignKey("groups.id", ondelete='CASCADE'))
    permissions = relationship(
        "Permission", secondary=permissions_groups, cascade="all,delete", back_populates ="groups", 
    )
    users = relationship(
        "User", secondary=users_groups, cascade="all,delete", back_populates ="groups"
    )
    def __str__(self):
        answer = "group " + self.name
        if self.parent_group is not None:
            answer = "sub-" + answer
        return answer

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return self.id
        
class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String, nullable=True, unique=True)
    groups = relationship(
        "Group", secondary=permissions_groups, cascade="all,delete", back_populates="permissions"
    )
    roles = relationship(
        "Role", secondary=permissions_roles, cascade="all,delete", back_populates="permissions"
    )

    def __str__(self):
        return self.namee   

    def __repr__(self) -> str:
        return self.name