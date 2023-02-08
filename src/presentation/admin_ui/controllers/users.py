from sqladmin import ModelView
from src.data_access.postgresql.tables import User, UserClaim


class UserAdminController(ModelView, model=User):
    column_list = [User.id, User.username, User.email,] #User.claims]

class UserClaimAdminController(ModelView, model=UserClaim):
    column_list = [UserClaim.user, UserClaim.claim_value, UserClaim.claim_type, ]