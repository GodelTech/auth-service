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


class ThirdPartyFacebookRequestModel(BaseModel):
    state: str
    response_type: Optional[str]
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyGoogleRequestModel(BaseModel):
    state: str
    code: Optional[str]
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyLinkedinRequestModel(BaseModel):
    state: str
    code: Optional[str]
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyMicrosoftRequestModel(BaseModel):
    state: str
    code: str

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


@dataclass
class StateRequestModel:
    state: str = Form(...)
