from typing import Union
from pydantic import BaseModel
from fastapi import Form
from dataclasses import dataclass


class RequestDefaultGroupModel(BaseModel):
    group_id: int = Form(...)
    class Config:
        orm_mode = True

@dataclass
class RequestGroupModel:
    group_id: int = Form(...)
    class Config:
        orm_mode = True


@dataclass
class RequestNewGroupModel:
    name: str = Form(...)
    parent_group: Union[None, int] = Form(None)
    class Config:
        orm_mode = True

@dataclass
class RequestUpdateGroupModel:
    group_id: int = Form(...)
    name: Union[None, str] = Form(None)
    parent_group: Union[None, int] = Form(None)
    class Config:
        orm_mode = True
