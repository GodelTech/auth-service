from dataclasses import dataclass
from typing import Optional

from fastapi import Form
from pydantic import BaseModel


class ThirdPartyOIDCRequestModel(BaseModel):
    code: str
    state: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyGoogleRequestModel(BaseModel):
    code: Optional[str]
    state: str
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyLinkedinRequestModel(BaseModel):
    code: Optional[str]
    state: str
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class ThirdPartyMicrosoftRequestModel(BaseModel):
    code: str
    state: str

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


@dataclass
class StateRequestModel:
    state: str = Form(...)


class ThirdPartyFacebookRequestModel(BaseModel):
    state: str
    response_type: Optional[str]
    scope: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"
