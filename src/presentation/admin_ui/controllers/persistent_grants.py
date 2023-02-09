from sqladmin import ModelView
from src.data_access.postgresql.tables import PersistentGrant, PersistentGrantTypes


class PersistentGrantAdminController(ModelView, model=PersistentGrant):
    column_list = [PersistentGrant.id, 
                   #PersistentGrant.client_id, 
                   PersistentGrant.data,
                   #PersistentGrant.type_of_grant
                   ]

class PersistentGrantTypesAdminController(ModelView, model=PersistentGrantTypes):
    column_list = [PersistentGrantTypes.id, PersistentGrantTypes.type_of_grant]