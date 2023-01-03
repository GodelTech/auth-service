from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy_utils import ChoiceType

from .base import BaseModel


class ApiResource(BaseModel):
    __tablename__ = "api_resources"

    description = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    enabled = Column(Boolean, default=True, nullable=True)
    name = Column(String, nullable=False)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiSecret(BaseModel):
    API_SECRET_TYPE = [("sha256", "Sha256"), ("sha512", "Sha512")]
    __tablename__ = "api_secrets"

    api_resources_id = Column(Integer, ForeignKey("api_resources.id"))
    description = Column(String, nullable=True)
    expiration = Column(DateTime, nullable=False)
    type = Column(ChoiceType(API_SECRET_TYPE))
    value = Column(String, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiClaim(BaseModel):
    API_CLAIM_TYPE = [("string", "String")]
    __tablename__ = "api_claims"

    api_resources_id = Column(Integer, ForeignKey("api_resources.id"))
    type = Column(ChoiceType(API_CLAIM_TYPE))

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiScope(BaseModel):
    __tablename__ = "api_scopes"

    api_resources_id = Column(Integer, ForeignKey("api_resources.id"))
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    emphasize = Column(Boolean, default=False, nullable=True)
    required = Column(Boolean, default=False, nullable=True)
    show_in_discovery_document = Column(Boolean, default=False, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiScopeClaim(BaseModel):
    API_SCOPE_CLAIM_TYPE = [
        ("name", "Name"),
        ("family_name", "Family Name"),
        ("middle_name", "Middle name"),
        ("nickname", "Nickname"),
        ("preferred_username", "Preferred username"),
        ("profile_picture", "Profile picture"),
        ("website", "Website"),
        ("gender", "Gender"),
        ("birthdate", "Birthdate"),
        ("zone_info", "Zone info"),
        ("locale", "Locale"),
        ("updated_at", "Updated at"),
    ]
    __tablename__ = "api_scope_claims"

    api_scopes_id = Column(Integer, ForeignKey("api_scopes.id"))
    type = Column(ChoiceType(API_SCOPE_CLAIM_TYPE))

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"
