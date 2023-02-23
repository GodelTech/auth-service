from typing import Union, Optional
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import Form

@dataclass
class RequestDefaultUserModel(BaseModel):

    class Config:
        orm_mode = True

class RequestUserModel(BaseModel):

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
    password:str = Form(...)

    def dictionary(self):
        return{
            "email":self.email,
            "security_stamp":self.security_stamp,
            "phone_number":self.phone_number,
            "two_factors_enabled":self.two_factors_enabled,
            "username":self.username,
            "password":self.password
        }

    class Config:
        orm_mode = True

@dataclass
class RequestGroupsUserModel:

    group_ids: str = Form(..., description='Example: "1,2,3"')

    class Config:
        orm_mode = True

@dataclass
class RequestRolesUserModel:    

    role_ids: str = Form(..., description='Example: "1,2,3"')

    class Config:
        orm_mode = True

        
@dataclass
class RequestPasswordUserModel:

    new_password: str = Form(...)

    class Config:
        orm_mode = True