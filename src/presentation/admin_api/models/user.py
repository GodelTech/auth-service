from typing import Union, Optional
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import Form

@dataclass
class RequestDefaultUserModel(BaseModel):
    user_id: int = Form(...)

    class Config:
        orm_mode = True

class RequestUserModel(BaseModel):

    user_id: int

    class Config:
        orm_mode = True


class RequestAllUserModel(BaseModel):
    group_id: Optional[int] 
    role_id: Optional[int]

    class Config:
        orm_mode = True


class ResponceAllUserModel(BaseModel):
    all_users: str

    class Config:
        orm_mode = True

@dataclass
class RequestUpdateUserModel:
    user_id: int = Form(...)
    username: Union[None, str] = Form(None)
    email: Union[None, str] = Form(None)
    email_confirmed: Union[None, bool] = Form(None)
    phone_number: Union[None, str] = Form(None)
    phone_number_confirmed: Union[None, bool] = Form(None)
    two_factors_enabled: Union[None, bool] = Form(None)
    lockout_end_date_utc: Union[None, str] = Form(None)
    lockout_enabled: Union[None, bool] = Form(None)
    
    class Config:
        orm_mode = True

@dataclass
class RequestCreateUserModel:
    email:str = Form(...)
    security_stamp:str = Form(...)
    phone_number:str = Form(...)
    two_factors_enabled:bool = Form(...)
    username:str = Form(...)
    # password:str = Form(...)

    def dictionary(self):
        return{
            "email":self.email,
            "security_stamp":self.security_stamp,
            "phone_number":self.phone_number,
            "two_factors_enabled":self.two_factors_enabled,
            "username":self.username,
        }

    class Config:
        orm_mode = True

@dataclass
class RequestGroupsUserModel:

    user_id: int = Form(...)
    group_ids: str = Form(..., description='Example: "1,2,3"')

    class Config:
        orm_mode = True

@dataclass
class RequestRolesUserModel:    
    user_id: int = Form(...)
    role_ids: str = Form(..., description='Example: "1,2,3"')

    class Config:
        orm_mode = True

        
@dataclass
class RequestPasswordUserModel:

    user_id: int = Form(...)
    new_password: str = Form(...)

    class Config:
        orm_mode = True