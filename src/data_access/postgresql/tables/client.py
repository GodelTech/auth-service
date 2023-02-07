import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
#from sqlalchemy_utils import ChoiceType

from .base import BaseModel

ACCESS_TOKEN_TYPES = ["jwt", "reference",]
PROTOCOL_TYPES = ["open_id_connect", "open_id_connect2"]
REFRESH_TOKEN_EXPIRATION = ["absolute", "sliding"]
REFRESH_TOKEN_USAGE = ["one_time_only", "reuse"]

class Client(BaseModel):

    

    __tablename__ = "clients"
    __table_args__ =  (
        CheckConstraint(sqltext= f'protocol_type IN {str(PROTOCOL_TYPES)[1:-1]}', name = "check1"),
        CheckConstraint(sqltext= f'refresh_token_expiration IN ({str(REFRESH_TOKEN_EXPIRATION)[1:-1]})', name = "check2"),
        CheckConstraint(sqltext= f'refresh_token_usage IN ({str(REFRESH_TOKEN_USAGE)[1:-1]})', name = "check3"),
        CheckConstraint(sqltext= f'access_token_type IN {str(ACCESS_TOKEN_TYPES)[1:-1]}', name = "check4")
        )
    client_id = Column(String(80), nullable=False, unique=True)
    absolute_refresh_token_lifetime = Column(
        Integer, default=2592000, nullable=False
    )
    access_token_lifetime = Column(Integer, default=3600, nullable=False)
    access_token_type = Column(String(),)
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
    protocol_type = Column(String(),)
    refresh_token_expiration = Column(String())
    refresh_token_usage = Column(String())
    require_client_secret = Column(Boolean, default=True, nullable=False)
    require_consent = Column(Boolean, default=True, nullable=False)
    require_pkce = Column(Boolean, default=False, nullable=False)
    sliding_refresh_token_lifetime = Column(
        Integer, default=1296000, nullable=False
    )
    update_access_token_claims_on_refresh = Column(
        Boolean, default=False, nullable=False
    )
    

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.client_name}"

    # __table_args__ =  (
    #     CheckConstraint(protocol_type.in_(PROTOCOL_TYPES)),
    #     CheckConstraint(refresh_token_expiration.in_(REFRESH_TOKEN_EXPIRATION)),
    #     CheckConstraint(refresh_token_usage.in_(REFRESH_TOKEN_USAGE)),
    #     CheckConstraint(access_token_type.in_(ACCESS_TOKEN_TYPES))
    #     )

class ClientIdRestriction(BaseModel):
    __tablename__ = "client_id_restrictions"

    provider = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.provider}"


class ClientClaim(BaseModel):
    __tablename__ = "client_claims"

    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.type}"


class ClientScope(BaseModel):
    __tablename__ = "client_scopes"

    scope = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientPostLogoutRedirectUri(BaseModel):
    __tablename__ = "client_post_logout_redirect_uris"

    post_logout_redirect_uri = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientCorsOrigin(BaseModel):
    __tablename__ = "client_cors_origins"

    origin = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientRedirectUri(BaseModel):
    __tablename__ = "client_redirect_uris"

    redirect_uri = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientGrantType(BaseModel):
    __tablename__ = "client_grant_types"

    grant_type = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientSecret(BaseModel):
    __tablename__ = "client_secrets"

    description = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.type}"


# def upgrade() -> None:
#     # ### commands auto generated by Alembic - please adjust! ###
#     op.create_check_constraint(
#         "protocol_type_in_list",
#         "clients",
#         f'"protocol_type" IN ({from_list_of_str_to_str(PROTOCOL_TYPES)})'
#     )
#     op.create_check_constraint(
#         "refresh_token_expiration_in_list",
#         "clients",
#         f'"refresh_token_expiration" IN ({from_list_of_str_to_str(REFRESH_TOKEN_EXPIRATION)})'
#     )
#     op.create_check_constraint(
#         "refresh_token_usage_in_list",
#         "clients",
#         f'"protocol_type" IN ({from_list_of_str_to_str(REFRESH_TOKEN_USAGE)})'
#     )
#     op.create_check_constraint(
#         "access_token_type_in_list",
#         "clients",
#         f'"access_token_type" IN ({from_list_of_str_to_str(ACCESS_TOKEN_TYPES)})'
#     )
    
#     # ### end Alembic commands ###


# def downgrade() -> None:
#     # ### commands auto generated by Alembic - please adjust! ###
#     op.drop_constraint("protocol_type_in_list", "clients", type_="check")
#     op.drop_constraint("refresh_token_expiration_in_list", "clients", type_="check")
#     op.drop_constraint("refresh_token_usage_in_list", "clients", type_="check")
#     op.drop_constraint("access_token_type_in_list", "clients", type_="check")
#     # ### end Alembic commands ###