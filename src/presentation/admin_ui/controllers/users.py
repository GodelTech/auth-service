from sqladmin import ModelView
from src.data_access.postgresql.tables import User


class UserAdminController(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.email_confirmed, User.phone_number,
                   User.claims]
