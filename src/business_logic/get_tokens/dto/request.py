from dataclasses import dataclass
from typing import Optional
from fastapi import Form
from pydantic import BaseModel


class RequestTokenModel(BaseModel):
    client_id: Optional[str]
    client_secret: Optional[str]
    grant_type: str
    scope: Optional[str]
    redirect_uri: Optional[str]
    code: Optional[str]
    code_verifier: Optional[str]
    username: Optional[str]
    password: Optional[str]
    acr_values: Optional[str]
    refresh_token: Optional[str]
    device_code: Optional[str]

    @classmethod
    def as_form(
            cls,
            client_id: Optional[str] = Form(...),
            client_secret: Optional[str] = Form(None),
            grant_type: str = Form(...),
            scope: str = Form(None),
            redirect_uri: Optional[str] = Form(None),
            code: Optional[str] = Form(None),
            code_verifier: Optional[str] = Form(None),
            username: Optional[str] = Form(None),
            password: Optional[str] = Form(None),
            acr_values: Optional[str] = Form(None),
            refresh_token: Optional[str] = Form(None),
            device_code: Optional[str] = Form(None)
    ) -> 'RequestTokenModel':
        return cls(client_id=client_id, client_secret=client_secret, grant_type=grant_type, scope=scope,
                   redirect_uri=redirect_uri, code=code, code_verifier=code_verifier, username=username,
                   password=password, acr_values=acr_values, refresh_token=refresh_token, device_code=device_code)
