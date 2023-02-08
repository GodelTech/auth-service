from sqladmin import ModelView
from src.data_access.postgresql.tables import User, UserClaim, UserClaimType


class UserAdminController(ModelView, model=User):
    column_list = [User.id, User.username,
                   User.claims]

class UserClaimAdminController(ModelView, model=UserClaim):
    column_list = [UserClaim.claim_type,
                   UserClaim.claim_value,
                   UserClaim.user]

class TypesUserClaimAdminController(ModelView, model=UserClaimType):
    column_list = [UserClaimType.type,]