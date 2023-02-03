from typing import Union
from pydantic import BaseModel
from fastapi import Form
from dataclasses import dataclass


class RequestRoleBaseModel(BaseModel):
    role_id: int = Form(...)
    class Config:
        orm_mode = True

@dataclass
class RequestRoleModel:
    role_id: int = Form(...)
    class Config:
        orm_mode = True


class RequestListRoleModel(BaseModel):
    role_ids: str = Form(...)
    class Config:
        orm_mode = True

@dataclass
class RequestNewRoleModel:
    name: str = Form(...)
    class Config:
        orm_mode = True

@dataclass
class RequestUpdateRoleModel:
    role_id: int  = Form(...)
    name: Union[None, str]  = Form(None)
    class Config:
        orm_mode = True
