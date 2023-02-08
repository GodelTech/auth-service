from sqladmin import ModelView
from src.data_access.postgresql.tables import UserClaim, User
from src.data_access.postgresql.tables import ChoiceUserClaimType

class UserClaimAdminController(ModelView, model=UserClaim):
    column_list = [
        UserClaim.user,
        UserClaim.claim_type, 
        UserClaim.claim_value,
        ]
    
class ChoiceUserClaimAdminController(ModelView, model=ChoiceUserClaimType):
    column_list = [
        ChoiceUserClaimType.id,
        ChoiceUserClaimType.type, 
        ChoiceUserClaimType.userclaim,
        ]