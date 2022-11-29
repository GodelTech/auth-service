from typing import List, Optional

from pydantic import BaseModel


class PostRequestModel(BaseModel):
    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    state: Optional[str]
    response_mode: Optional[str]
    nonce: Optional[str]
    display: Optional[str]
    prompt: Optional[str]
    max_age: Optional[int]
    ui_locales: Optional[str]
    id_token_hint: Optional[str]
    login_hint: Optional[str]
    acr_values: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.client_id}"


class ResponseAuthorizationModel(BaseModel):
    code: str
    state: str

    class Config:
        orm_mode = True
