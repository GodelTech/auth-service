from sqladmin import ModelView
from src.data_access.postgresql.tables import User, UserClaim, UserClaimType, UserLogin


class UserAdminController(ModelView, model=User,):
    icon = "fa-solid fa-user"
    column_list = [User.id, User.username,
                   User.claims]

class UserClaimAdminController(ModelView, model=UserClaim):
    icon = "fa-solid fa-user"
    column_list = [UserClaim.claim_type,
                   UserClaim.claim_value,
                   UserClaim.user]

class TypesUserClaimAdminController(ModelView, model=UserClaimType):
    icon = "fa-solid fa-user"
    column_list = [
        UserClaimType.id, 
        UserClaimType.type_of_claim,
        ]