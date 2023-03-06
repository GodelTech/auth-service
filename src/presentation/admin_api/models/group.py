from typing import Union
from pydantic import BaseModel
from fastapi import Form
from dataclasses import dataclass



@dataclass
class RequestNewGroupModel:
    name: str = Form(...)
    parent_group: Union[None, int] = Form(None)
    class Config:
        orm_mode = True

@dataclass
class RequestUpdateGroupModel:
    name: Union[None, str] = Form(None)
    parent_group: Union[None, int] = Form(None)
    class Config:
        orm_mode = True
