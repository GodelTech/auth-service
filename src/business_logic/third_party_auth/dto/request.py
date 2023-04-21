from typing import Optional

from fastapi import Form
from pydantic import BaseModel


# * It's checked and matching with :
# * - GitHub
# * - Linkedin also use same data, but it is said, that it's mandatory, so i suppose we can use that model
# * - Gitlab same as linkedin
# TODO -> check if it'll be a good solution to add response_type here(linkedin, gitlab, microsoft, google)
class ThirdPartyAccessTokenRequestModelBase(BaseModel):
    code: str
    state: str

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


class StateRequestModel(BaseModel):
    state: str

    @classmethod
    def as_form(cls, state: str = Form(...)) -> "StateRequestModel":
        return cls(state=state)
