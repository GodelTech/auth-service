from sqladmin import ModelView
from src.data_access.postgresql.tables import Permission


class PermissionAdminController(ModelView, model=Permission):
    column_list = [Permission.id, Permission.name,]
