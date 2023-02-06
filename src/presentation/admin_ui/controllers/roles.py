from sqladmin import ModelView
from src.data_access.postgresql.tables import Role


class RoleAdminController(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.created_at]

