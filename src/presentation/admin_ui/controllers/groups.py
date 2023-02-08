from sqladmin import ModelView
from src.data_access.postgresql.tables import Group


class GroupAdminController(ModelView, model=Group):
    column_list = [Group.id, Group.name, Group.parent_group,]
