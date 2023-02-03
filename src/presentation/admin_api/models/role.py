from typing import Union
from pydantic import BaseModel


class RequestRoleModel(BaseModel):
    role_id: int
    class Config:
        orm_mode = True

class RequestListRoleModel(BaseModel):
    role_ids: list[int]
    class Config:
        orm_mode = True

class RequestNewRoleModel(BaseModel):
    name: str
    class Config:
        orm_mode = True

class RequestUpdateRoleModel(BaseModel):
    role_id: int
    name: Union[None, str]
    class Config:
        orm_mode = True
