from pydantic import BaseModel
from typing import Optional, Union
from dataclasses import dataclass
from fastapi import Form


@dataclass
class ClientRequestModel():
    redirect_uris: list[str] = Form(...)
    client_name: str = Form(...)
    client_uri: str = Form(...)
    logo_uri: str = Form(...)
    grant_types: list[str] = Form(default=["authorization_code"])
    response_types: list[str] = Form(default=["code"])
    token_endpoint_auth_method: str = Form(default="client_secret_post")
    scope: str = Form(default="openid profile")
    class Config:
        orm_mode = True

class ClientResponseModel(BaseModel):
    client_id: str
    client_secret: str
    class Config:
        orm_mode = True

@dataclass
class ClientUpdateRequestModel():
    redirect_uris: Union[None, list[str]] = Form(None)
    client_name: Union[None, str] = Form(None)
    client_uri: Union[None, str] = Form(None)
    logo_uri: Union[None, str] = Form(None)
    grant_types: Union[None, list[str]] = Form(None)
    response_types: Union[None, list[str]] = Form(None)
    token_endpoint_auth_method: Union[None, str] = Form(None)
    scope: Union[None, str] = Form(None)
    class Config:
        orm_mode = True
