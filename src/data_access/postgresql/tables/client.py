import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
#from sqlalchemy_utils import ChoiceType

from .base import BaseModel, Base


class Client(BaseModel):

    __tablename__ = "clients"

    client_id = Column(String(80), nullable=False, unique=True)
    absolute_refresh_token_lifetime = Column(
        Integer, default=2592000, nullable=False
    )
    access_token_lifetime = Column(Integer, default=3600, nullable=False)
    access_token_type_id = Column(Integer, ForeignKey("access_token_types.id", ondelete='CASCADE'), nullable=False)
    access_token_type = relationship("AccessTokenType",  backref="client", foreign_keys="Client.access_token_type_id")
    allow_access_token_via_browser = Column(
        Boolean, default=False, nullable=False
    )
    allow_offline_access = Column(Boolean, default=False, nullable=False)
    allow_plain_text_pkce = Column(Boolean, default=False, nullable=False)
    allow_remember_consent = Column(Boolean, default=True, nullable=False)
    always_include_user_claims_id_token = Column(
        Boolean, default=False, nullable=False
    )
    always_send_client_claims = Column(Boolean, default=False, nullable=False)
    authorisation_code_lifetime = Column(Integer, default=300, nullable=False)
    client_name = Column(String(50), nullable=False)
    client_uri = Column(String(65), nullable=False)
    enable_local_login = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    identity_token_lifetime = Column(Integer, default=300, nullable=False)
    include_jwt_id = Column(Boolean, default=False, nullable=False)
    logo_uri = Column(String, nullable=False)
    logout_session_required = Column(Boolean, nullable=False)
    logout_uri = Column(String, nullable=False)
    prefix_client_claims = Column(String)
    
    protocol_type_id = Column(Integer, ForeignKey("protocol_types.id", ondelete='CASCADE'), nullable=False)
    protocol_type = relationship("ProtocolType",  backref="client", foreign_keys="Client.protocol_type_id")

    refresh_token_expiration_type_id = Column(Integer, ForeignKey("refresh_token_expiration_types.id", ondelete='CASCADE'), nullable=False)
    refresh_token_expiration_type = relationship("RefreshTokenExpirationType",  backref="client", foreign_keys="Client.refresh_token_expiration_type_id")

    refresh_token_usage_type_id = Column(Integer, ForeignKey("refresh_token_usage_types.id", ondelete='CASCADE'), nullable=False)
    refresh_token_usage_type = relationship("RefreshTokenUsageType",  backref="client", foreign_keys="Client.refresh_token_usage_type_id")

    require_client_secret = Column(Boolean, default=True, nullable=False)
    require_consent = Column(Boolean, default=True, nullable=False)
    require_pkce = Column(Boolean, default=False, nullable=False)
    sliding_refresh_token_lifetime = Column(
        Integer, default=1296000, nullable=False
    )
    update_access_token_claims_on_refresh = Column(
        Boolean, default=False, nullable=False
    )
    grants = relationship("PersistentGrant", back_populates = "client", foreign_keys = "PersistentGrant.client_id")

    def __str__(self) -> str:
        return f"{self.id} id: {self.client_name}"

    def __repr__(self) -> str:
        return f"{self.id} id: {self.client_name}"

class AccessTokenType(Base):
    __tablename__ = "access_token_types"
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"{self.type}"

class ProtocolType(Base):
    __tablename__ = 'protocol_types'
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"{self.type}"

class RefreshTokenExpirationType(Base):
    __tablename__ = 'refresh_token_expiration_types'
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"{self.type}"
    
class RefreshTokenUsageType(Base):
    __tablename__ = 'refresh_token_usage_types'
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return f"{self.type}"


class ClientIdRestriction(BaseModel):
    __tablename__ = "client_id_restrictions"

    provider = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "id_restrictions",)
    def __repr__(self) -> str:
        return f"{self.provider}"


class ClientClaim(BaseModel):
    __tablename__ = "client_claims"

    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "claims",)
    def __repr__(self) -> str:
        return f"{self.type}"


class ClientScope(BaseModel):
    __tablename__ = "client_scopes"

    scope = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "scopes",)
    def __str__(self) -> str:
        return f"{self.scope}"

    def __repr__(self) -> str:
        return f"{self.scope}"


class ClientPostLogoutRedirectUri(BaseModel):
    __tablename__ = "client_post_logout_redirect_uris"

    post_logout_redirect_uri = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "post_logout_redirect_uris",)

    def __str__(self) -> str:
        return f"{self.post_logout_redirect_uri}"
    
    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientCorsOrigin(BaseModel):
    __tablename__ = "client_cors_origins"

    origin = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "cors_origins",)
    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientRedirectUri(BaseModel):
    __tablename__ = "client_redirect_uris"

    redirect_uri = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "redirect_uris",)
    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientGrantType(BaseModel):
    __tablename__ = "client_grant_types"

    grant_type = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "grant_types",)
    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientSecret(BaseModel):
    __tablename__ = "client_secrets"

    description = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete='CASCADE'))
    client = relationship("Client", backref = "secrets",)
    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.type}"
