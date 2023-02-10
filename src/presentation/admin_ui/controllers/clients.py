from sqladmin import ModelView
from src.data_access.postgresql.tables.client import *


class ClientAdminController(ModelView, model=Client):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [Client.client_id, Client.client_name, Client.client_uri, Client.created_at]

class AccessTokenTypeAdminController(ModelView, model=AccessTokenType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [AccessTokenType.id, AccessTokenType.type,]

class ProtocolTypeController(ModelView, model=ProtocolType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ProtocolType.id, ProtocolType.type]

class RefreshTokenUsageTypeController(ModelView, model=RefreshTokenUsageType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [RefreshTokenUsageType.id, RefreshTokenUsageType.type]

class RefreshTokenExpirationTypeController(ModelView, model=RefreshTokenExpirationType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [RefreshTokenExpirationType.id, RefreshTokenExpirationType.type]




class ClientIdRestrictionController(ModelView, model=ClientIdRestriction):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientIdRestriction.id, 
                   ClientIdRestriction.provider]

class ClientClaimController(ModelView, model=ClientClaim):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientClaim.id, 
                   ClientClaim.type,
                   ClientClaim.value
                   ]

class ClientPostLogoutRedirectUriController(ModelView, model=ClientPostLogoutRedirectUri):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientPostLogoutRedirectUri.id, 
                   ClientPostLogoutRedirectUri.post_logout_redirect_uri]

class ClientCorsOriginController(ModelView, model=ClientCorsOrigin):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientCorsOrigin.id, 
                   ClientCorsOrigin.origin
                   ]

class ClientRedirectUriController(ModelView, model=ClientRedirectUri):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientRedirectUri.id, 
                   ClientRedirectUri.redirect_uri]

class ClientGrantTypeController(ModelView, model=ClientGrantType):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [ClientGrantType.id, 
                   ClientGrantType.grant_type]

class ClientSecretController(ModelView, model=ClientSecret):
    icon = "fa-solid fa-mobile-screen-button"
    column_list = [
        ClientSecret.id, 
        ClientSecret.type,
        ClientSecret.description,
        ClientSecret.expiration,
        ClientSecret.type,
        ClientSecret.value,
        ]

