from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .base import BaseModel

class ApiResources(BaseModel):
    __tablename__ = "api_resources"

    description = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    enabled = Column(Boolean, default=True, nullable=True)
    name = Column(String, nullable=False)
    
    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"

class ApiSecrets(BaseModel):
    __tablename__ = "api_secrets"

    api_resources_id = Column("ApiResources", Integer, ForeignKey('ApiResources.id'))
    description = Column(String, nullable=True)
    expiration = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"

class ApiClaims(BaseModel):
    __tablename__ = "api_slaims"
    
    api_resources_id = Column("ApiResources", Integer, ForeignKey('ApiResources.id'))
    type = Column(String, nullable=False)
    
    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"

class ApiScopes(BaseModel):
    __tablename__ = "api_scopes"
    
    api_resources_id = Column("ApiResources", Integer, ForeignKey('ApiResources.id'))
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    emphasize = Column(Boolean, default=False, nullable=True)
    required = Column(Boolean, default=False, nullable=True)
    show_in_discovery_document = Column(Boolean, default=False,  nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"

class ApiScopeClaim(BaseModel):
    __tablename__ = "api_scope_claims"
    
    api_scopes_id = Column("ApiScopes", Integer, ForeignKey('ApiScopes.id'))
    type = Column(String, nullable=True)

    def __str__(self):
        return f"Model {self.__tablename__}: {self.id}"
