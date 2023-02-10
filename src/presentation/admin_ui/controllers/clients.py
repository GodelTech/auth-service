from sqladmin import ModelView
from src.data_access.postgresql.tables import Client, AccessTokenType, RefreshTokenUsageType, ProtocolType, RefreshTokenExpirationType


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