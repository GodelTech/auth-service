from sqladmin import ModelView
from src.data_access.postgresql.tables import Client, AccessTokenType, RefreshTokenUsageType, ProtocolType, RefreshTokenExpirationType


class ClientAdminController(ModelView, model=Client):
    column_list = [Client.client_id, Client.client_name, Client.client_uri, Client.created_at]

class AccessTokenTypeAdminController(ModelView, model=AccessTokenType):
    column_list = [AccessTokenType.id, AccessTokenType.type,]

class ProtocolTypeController(ModelView, model=ProtocolType):
    column_list = [ProtocolType.id, ProtocolType.type]

class RefreshTokenUsageTypeController(ModelView, model=RefreshTokenUsageType):
    column_list = [RefreshTokenUsageType.id, RefreshTokenUsageType.type]

class RefreshTokenExpirationTypeController(ModelView, model=RefreshTokenExpirationType):
    column_list = [RefreshTokenExpirationType.id, RefreshTokenExpirationType.type]