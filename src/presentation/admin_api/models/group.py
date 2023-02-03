from typing import Union
from pydantic import BaseModel


class RequestGroupModel(BaseModel):
    group_id: int
    class Config:
        orm_mode = True


class RequestNewGroupModel(BaseModel):
    name: str
    parent_group: Union[None, int]
    class Config:
        orm_mode = True

class RequestUpdateGroupModel(BaseModel):
    group_id: int
    name: Union[None, str]
    parent_group: Union[None, int]
    class Config:
        orm_mode = True
