import datetime

from sqlalchemy import String, Integer, Column, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, unique=True)
    client_id = Column(String, nullable=False, unique=True)
    absolute_refresh_token_lifetime = Column(Integer, default=2592000, nullable=False)
    access_token_lifetime = Column(Integer, default=3600, nullable=False)
    access_token_type = Column(String, default='Jwt', nullable=False)
    allow_access_token_via_browser = Column(Boolean, default=False, nullable=False)
    allow_offline_access = Column(Boolean, default=False, nullable=False)
    allow_plain_text_pkce = Column(Boolean, default=False, nullable=False)
    allow_remember_consent = Column(Boolean, default=True, nullable=False)
    always_include_user_claims_id_token = Column(Boolean, default=False, nullable=False)
    always_send_client_claims = Column(Boolean, default=False, nullable=False)
    authorisation_code_lifetime = Column(Integer, default=300, nullable=False)
    client_name = Column(String, nullable=False)
    client_uri = Column(String, nullable=False)
    enable_local_login = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    identity_token_lifetime = Column(Integer, default=300, nullable=False)
    include_jwt_id = Column(Boolean, default=False, nullable=False)
    logo_uri = Column(String, nullable=False)
    logout_session_required = Column(Boolean, nullable=False)
    logout_uri = Column(String, nullable=False)
    prefix_client_claims = Column(String)
    protocol_type = Column(String, default='OpenID Connect', nullable=False)
    refresh_token_expiration = Column(String, default='Absolute', nullable=False)
    refresh_token_usage = Column(String, default='OneTimeOnly', nullable=False)
    require_client_secret = Column(Boolean, default=True, nullable=False)
    require_consent = Column(Boolean, default=True, nullable=False)
    require_pkce = Column(Boolean, default=False, nullable=False)
    sliding_refresh_token_lifetime = Column(Integer, default=1296000, nullable=False)
    update_access_token_claims_on_refresh = Column(Boolean, default=False, nullable=False)
    created = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.client_name}"


class ClientIdRestriction(Base):
    __tablename__ = "client_id_restrictions"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    client_id = Column(ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.provider}"


class ClientClaim(Base):
    __tablename__ = "client_claims"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.type}"


class ClientScope(Base):
    __tablename__ = "client_scopes"

    id = Column(Integer, primary_key=True)
    scope = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientPostLogoutRedirectUri(Base):
    __tablename__ = "client_post_logout_redirect_uris"

    id = Column(Integer, primary_key=True)
    post_logout_redirect_uri = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientCorsOrigin(Base):
    __tablename__ = "client_cors_origins"

    id = Column(Integer, primary_key=True)
    origin = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientRedirectUri(Base):
    __tablename__ = "client_redirect_uris"

    id = Column(Integer, primary_key=True, unique=True)
    redirect_uri = Column(String, nullable=False)
    client_id = Column(ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientGrantType(Base):
    __tablename__ = "client_grant_types"

    id = Column(Integer, primary_key=True, unique=True)
    grant_type = Column(String, nullable=False)
    client_id = Column(ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientSecret(Base):
    __tablename__ = "client_secrets"

    id = Column(Integer, primary_key=True, unique=True)
    description = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(ForeignKey("clients.client_id"))

    def __repr__(self):
        return f"Model {self.__class__.__name__}: {self.type}"
