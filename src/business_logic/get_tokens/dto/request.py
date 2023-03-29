from dataclasses import dataclass
from typing import Optional
from fastapi import Form


@dataclass
class RequestTokenModel:
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
