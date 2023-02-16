from sqladmin import ModelView
from src.data_access.postgresql.tables import Group, Permission


class GroupAdminController(ModelView, model=Group):
    icon = "fa-solid fa-users"
    column_list = [ Group.id, 
                    Group.name,
                    Group.users,
                    Group.parent_group,
                    Group.permissions,
                   ]

class PermissionAdminController(ModelView, model=Permission):
    icon = "fa-solid fa-hand-fist"
    column_list = [ Permission.id, 
                    Permission.name,
                    Permission.groups,
                    Permission.roles,
                   ]


