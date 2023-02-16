from .auth import AdminAuthController
from .clients import (
    ClientAdminController,
    AccessTokenTypeAdminController,
    ProtocolTypeController,
    RefreshTokenUsageTypeController,
    RefreshTokenExpirationTypeController,
    ClientSecretController,
    ClientGrantTypeController,
    ClientRedirectUriController,
    ClientCorsOriginController,
    ClientPostLogoutRedirectUriController,
    ClientClaimController,
    ClientIdRestrictionController,
    )
from .users import (
    UserAdminController, 
    UserClaimAdminController, 
    TypesUserClaimAdminController, 
    )
from .persistent_grants import PersistentGrantAdminController, PersistentGrantTypeAdminController
from .roles import RoleAdminController
from .resources_related import (
    ApiResourceAdminController,
    ApiSecretAdminController,
    ApiSecretTypeAdminController,
    ApiClaimAdminController,
    ApiClaimTypeAdminController,
    ApiScopeAdminController,
    ApiScopeClaimAdminController,
    ApiScopeClaimTypeAdminController,
)
from .identity_resource import (
    IdentityResourceAdminController, 
    IdentityClaimAdminController, 
    IdentityProviderMappedAdminController,
    IdentityProviderAdminController,
    )
from .group import PermissionAdminController, GroupAdminController
from .device import DeviceAdminController



from sqladmin import ModelView
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column
import mock

Base = declarative_base()
class Line(Base):
    icon = "/home/danya/Desktop/identity-server-poc/login.png"
    __tablename__ = "Line"
    id = Column(Boolean, primary_key = True)

    
class SeparationLine(ModelView, model = Line):
    name_plural = " "
