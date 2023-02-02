from typing import Union
from pydantic import BaseModel

class RequestDefaultUserModel(BaseModel):

    user_id: int

    class Config:
        orm_mode = True

class RequestAllUserModel(BaseModel):
    group_id: Union[int, None]
    role_id: Union[int, None]

    class Config:
        orm_mode = True

class ResponceAllUserModel(BaseModel):
    all_users: list

    class Config:
        orm_mode = True

class RequestUpdateUserModel(BaseModel):
    user_id: int
    username: Union[None, str]
    email: Union[None, str]
    email_confirmed: Union[None, bool] 
    phone_number: Union[None, str]
    phone_number_confirmed: Union[None, bool]
    two_factors_enabled: Union[None, bool]
    lockout_end_date_utc: Union[None, str]
    lockout_enabled: Union[None, bool]
    
    class Config:
        orm_mode = True

class RequestCreateUserModel(BaseModel):
    email:str
    security_stamp:str
    phone_number:str 
    two_factors_enabled:bool 
    username:str 
    password:str 

    def __dict__(self):
        return{
            "email":self.email,
            "security_stamp":self.security_stamp,
            "phone_number":self.phone_number,
            "two_factors_enabled":self.two_factors_enabled,
            "username":self.username,
            #"password":self.password
        }

    class Config:
        orm_mode = True

class RequestGroupsUserModel(BaseModel):

    user_id: int 
    group_ids: list[int]

    class Config:
        orm_mode = True

class RequestRolesUserModel(BaseModel):    
    user_id: int 
    role_ids: list[int] 

    class Config:
        orm_mode = True

        
class RequestPasswordUserModel(BaseModel):

    user_id: int 
    new_password: str

    class Config:
        orm_mode = True