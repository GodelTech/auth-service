from sqladmin import ModelView
from src.data_access.postgresql.tables import Role


class RoleAdminController(ModelView, model=Role):
    icon = "fa-solid fa-id-card-clip"
    column_list = [Role.id, Role.name, Role.created_at]

