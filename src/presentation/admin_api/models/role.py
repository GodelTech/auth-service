from typing import Union
from pydantic import BaseModel
from fastapi import Form
from dataclasses import dataclass



@dataclass
class RequestNewRoleModel:
    name: str = Form(...)
    class Config:
        orm_mode = True

@dataclass
class RequestUpdateRoleModel:
    name: Union[None, str]  = Form(None)
    class Config:
        orm_mode = True
