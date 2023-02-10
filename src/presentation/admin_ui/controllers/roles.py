from sqladmin import ModelView
from src.data_access.postgresql.tables import Role


class RoleAdminController(ModelView, model=Role):
    icone ="fa-solid fa-id-badge"
    column_list = [Role.id, Role.name, Role.created_at]

