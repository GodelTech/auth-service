from dataclasses import dataclass
from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel


class ThirdPartyOIDCRequestModel(BaseModel):
    code: str
    state: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


@dataclass
class StateRequestModel:
    state: str = Form(...)
