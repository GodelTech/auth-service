from sqladmin import ModelView
from src.data_access.postgresql.tables import Client


class ClientAdminController(ModelView, model=Client):
    column_list = [Client.client_id, Client.client_name, Client.client_uri, Client.created_at]
