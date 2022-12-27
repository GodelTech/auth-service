from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import Form


class RequestRevokeModel(BaseModel):
    
    authorization: str

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


@dataclass
class BodyRequestRevokeModel:
    
    token: str = Form(...)

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"

