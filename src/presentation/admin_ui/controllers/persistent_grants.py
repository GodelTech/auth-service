from sqladmin import ModelView
from src.data_access.postgresql.tables import PersistentGrant, PersistentGrantType


class PersistentGrantAdminController(ModelView, model=PersistentGrant):
    icon = "fa-solid fa-key"
    column_list = [PersistentGrant.id, 
                  # PersistentGrant.client_id, 
                   PersistentGrant.expiration,
                   PersistentGrant.grant_data
                   ]

class PersistentGrantTypeAdminController(ModelView, model=PersistentGrantType):
    icon = "fa-solid fa-key"
    column_list = [PersistentGrantType.id, PersistentGrantType.type_of_grant]