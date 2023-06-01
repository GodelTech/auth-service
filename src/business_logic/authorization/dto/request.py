from typing import Optional

from fastapi import Form
from pydantic import BaseModel, SecretStr


class RequestModel(BaseModel):
    """
    Represents a GET method request model for authentication.

    Reference: https://www.rfc-editor.org/rfc/rfc6749#section-4
    """

    client_id: str
    response_type: str
    scope: str = "openid"
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
    user_code: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}: {self.client_id}"  # pragma: no coverage


class AuthRequestModel(BaseModel):
    """
    Represents a POST method request model for authentication.

    Reference: https://www.rfc-editor.org/rfc/rfc6749#section-4
    """

    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    username: str
    password: SecretStr
    user_code: Optional[str]
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

    @classmethod
    def as_form(
        cls,
        client_id: str = Form(...),
        response_type: str = Form(...),
        scope: str = Form(...),
        redirect_uri: str = Form(...),
        username: str = Form(...),
        password: SecretStr = Form(...),
        user_code: Optional[str] = Form(None),
        state: Optional[str] = Form(None),
        response_mode: Optional[str] = Form(None),
        nonce: Optional[str] = Form(None),
        display: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        max_age: Optional[int] = Form(None),
        ui_locales: Optional[str] = Form(None),
        id_token_hint: Optional[str] = Form(None),
        login_hint: Optional[str] = Form(None),
        acr_values: Optional[str] = Form(None),
    ) -> "AuthRequestModel":
        return cls(
            client_id=client_id,
            response_type=response_type,
            scope=scope,
            redirect_uri=redirect_uri,
            username=username,
            password=password,
            user_code=user_code,
            state=state,
            response_mode=response_mode,
            nonce=nonce,
            display=display,
            prompt=prompt,
            max_age=max_age,
            ui_locales=ui_locales,
            id_token_hint=id_token_hint,
            login_hint=login_hint,
            acr_values=acr_values,
        )
