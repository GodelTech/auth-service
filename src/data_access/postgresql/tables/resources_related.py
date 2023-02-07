from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, CheckConstraint


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

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiSecret(BaseModel):
   
    __tablename__ = "api_secrets"
    __table_args__ =  (
                    CheckConstraint(
                    sqltext= f'"type" IN {str(API_SECRET_TYPE)[1:-1]}', 
                    name = "types_in_list"
                    ),)
    api_resources_id = Column(Integer, ForeignKey("api_resources.id", ondelete='CASCADE'))
    description = Column(String, nullable=True)
    expiration = Column(DateTime, nullable=False)
    type = Column(String(10))
    value = Column(String, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiClaim(BaseModel):
    
    __tablename__ = "api_claims"
    __table_args__ =  (
                    CheckConstraint(
                    sqltext= f'"type" IN {str(API_CLAIM_TYPE)[1:-1]}', 
                    name = "types_claim_in_list"
                    ),)
    
    api_resources_id = Column(Integer, ForeignKey("api_resources.id", ondelete='CASCADE'))
    type = Column(String)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiScope(BaseModel):
    __tablename__ = "api_scopes"

    api_resources_id = Column(Integer, ForeignKey("api_resources.id", ondelete='CASCADE'))
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    emphasize = Column(Boolean, default=False, nullable=True)
    required = Column(Boolean, default=False, nullable=True)
    show_in_discovery_document = Column(Boolean, default=False, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"


class ApiScopeClaim(BaseModel):
    
    __tablename__ = "api_scope_claims"
    __table_args__ =  (
                    CheckConstraint(
                    sqltext= f'"type" IN {str(API_SCOPE_CLAIM_TYPE)[1:-1]}', 
                    name = "types_scope_claim_in_list"
                    ),)
    
    api_scopes_id = Column(Integer, ForeignKey("api_scopes.id", ondelete='CASCADE'))
    type = Column(String)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"
