from sqladmin import ModelView
from src.data_access.postgresql.tables import PersistentGrant, PersistentGrantTypes


class PersistentGrantAdminController(ModelView, model=PersistentGrant):
    icon = "fa-solid fa-key"
    column_list = [PersistentGrant.id, 
                   #PersistentGrant.client_id, 
                   PersistentGrant.data,
                   #PersistentGrant.persistent_grant_type_id
                   ]

class PersistentGrantTypesAdminController(ModelView, model=PersistentGrantTypes):
    icon = "fa-solid fa-key"
    column_list = [PersistentGrantTypes.id, PersistentGrantTypes.type_of_grant]