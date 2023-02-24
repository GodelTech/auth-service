from dataclasses import dataclass
from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel


class RequestModel(BaseModel):
    client_id: str
    response_type: str
    scope: Optional[str]
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
    code_challenge: Optional[str]
    code_challenge_method: Optional[str]
    
    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.client_id}"


class ResponseAuthorizationModel(BaseModel):
    code: str
    state: str

    class Config:
        orm_mode = True


@dataclass
class DataRequestModel:
    client_id: str = Form(...)
    response_type: str = Form(...)
    scope: str = Form(...)
    redirect_uri: str = Form(...)
    state: str = Form(None)
    response_mode: str = Form(None)
    nonce: str = Form(None)
    display: str = Form(None)
    prompt: str = Form(None)
    max_age: int = Form(None)
    ui_locales: str = Form(None)
    id_token_hint: str = Form(None)
    login_hint: str = Form(None)
    acr_values: str = Form(None)
    code_challenge: str = Form(None)
    code_challenge_method: str = Form(None)
    