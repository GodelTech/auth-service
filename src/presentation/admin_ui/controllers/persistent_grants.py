from sqladmin import ModelView
from src.data_access.postgresql.tables import PersistentGrant


class PersistentGrantAdminController(ModelView, model=PersistentGrant):
    column_list = [PersistentGrant.id, PersistentGrant.client_id, PersistentGrant.type, PersistentGrant.data,
                   PersistentGrant.expiration]
