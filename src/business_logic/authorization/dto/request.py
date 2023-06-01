from typing import Optional

from fastapi import Form
from pydantic import BaseModel, SecretStr


class RequestModel(BaseModel):
    """
    Represents a GET method request model for authentication.

    Attributes:
        client_id (str): The client identifier.
        response_type (str): The type of the response requested.
        scope (str): The scope of the access request (default: "openid").
        redirect_uri (str): The URI to redirect to after completing the request.
        state (Optional[str]): An optional opaque value used to maintain state between the request and the callback.
        response_mode (Optional[str]): An optional value indicating the response mode to be used.
        nonce (Optional[str]): An optional value used to associate a user agent session with an ID Token.
        display (Optional[str]): An optional value indicating how the authorization server displays the authentication and consent pages.
        prompt (Optional[str]): An optional value specifying whether the authorization server prompts the user for reauthentication and consent.
        max_age (Optional[int]): An optional value indicating the maximum elapsed time in seconds since the last time the user was actively authenticated.
        ui_locales (Optional[str]): An optional value specifying the end-user's preferred languages and scripts.
        id_token_hint (Optional[str]): An optional value used to pass an ID Token for pre-authentication.
        login_hint (Optional[str]): An optional value indicating the user's email address or other login identifier.
        acr_values (Optional[str]): An optional value specifying the requested Authentication Context Class Reference values.
        user_code (Optional[str]): An optional value representing a user code.


    Reference: https://openid.net/specs/openid-connect-core-1_0.html
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

     Attributes:
        client_id (str): The client identifier.
        response_type (str): The type of the response requested.
        scope (str): The scope of the access request.
        redirect_uri (str): The URI to redirect to after completing the request.
        username (str): The username for authentication.
        password (SecretStr): The password for authentication.
        user_code (Optional[str]): An optional value representing a user code.
        state (Optional[str]): An optional opaque value used to maintain state between the request and the callback.
        response_mode (Optional[str]): An optional value indicating the response mode to be used.
        nonce (Optional[str]): An optional value used to associate a user agent session with an ID Token.
        display (Optional[str]): An optional value indicating how the authorization server displays the authentication and consent pages.
        prompt (Optional[str]): An optional value specifying whether the authorization server prompts the user for reauthentication and consent.
        max_age (Optional[int]): An optional value indicating the maximum elapsed time in seconds since the last time the user was actively authenticated.
        ui_locales (Optional[str]): An optional value specifying the end-user's preferred languages and scripts.
        id_token_hint (Optional[str]): An optional value used to pass an ID Token for pre-authentication.
        login_hint (Optional[str]): An optional value indicating the user's email address or other login identifier.
        acr_values (Optional[str]): An optional value specifying the requested Authentication Context Class Reference values.


    Reference: https://openid.net/specs/openid-connect-core-1_0.html
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
