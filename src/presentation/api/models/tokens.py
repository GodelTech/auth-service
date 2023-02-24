from dataclasses import dataclass
from typing import Optional
from typing import Union
from fastapi import Form
from pydantic import BaseModel


@dataclass
class BodyRequestTokenModel:
    client_id: Optional[str] = Form(...)
    client_secret: Optional[str] = Form(None)
    grant_type: str = Form(...)
    scope: str = Form(None)
    redirect_uri: Optional[str] = Form(None)
    code: Optional[str] = Form(None)
    code_verifier: Optional[str] = Form(None)
    username: Optional[str] = Form(None)
    password: Optional[str] = Form(None)
    acr_values: Optional[str] = Form(None)
    refresh_token: Optional[str] = Form(None)
    device_code: Optional[str] = Form(None)

    class Config:
        orm_mode = True


class ResponseTokenModel(BaseModel):

    access_token: Optional[str]
    token_type: Optional[str]
    refresh_token: Optional[str]
    expires_in: Optional[int]
    id_token: Optional[str]
    refresh_expires_in : Optional[int]
    not_before_policy : Optional[int]
    scope : Optional[Union[list[str], str]]
    
    class Config:
        orm_mode = True