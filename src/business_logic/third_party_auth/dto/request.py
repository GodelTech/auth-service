from fastapi import Form
from pydantic import BaseModel


class ThirdPartyAccessTokenRequestModel(BaseModel):
    code: str
    state: str
    grant_type: str = "authorization_code"
    scope: str = "openid"
    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class StateRequestModel(BaseModel):
    state: str

    @classmethod
    def as_form(cls, state: str = Form(...)) -> "StateRequestModel":
        return cls(state=state)
