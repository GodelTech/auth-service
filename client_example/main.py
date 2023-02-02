from typing import Union
from urllib.parse import urlencode

import requests
from fastapi import FastAPI, Header
from fastapi.responses import RedirectResponse

from .httpx_oauth.openid import OpenID

client = OpenID(
    client_id="test_client",
    client_secret="past",
    openid_configuration_endpoint="http://localhost:8000/.well-known/openid-configuration",
)

app = FastAPI()

# Identity Server endpoints
AUTH_URL = "http://localhost:8000/authorize/"
TOKEN_URL = "http://localhost:8000/token/"
USERINFO_URL = "http://localhost:8000/userinfo/"


@app.get("/login")
async def get_login_form(
    authorization: Union[str, None] = Header(default=None)
):
    if authorization:
        access_token = authorization.split(" ")[-1]
        # verify token
        # ...
        # if valid:
        return RedirectResponse("http://localhost:8001/")
    params = {
        "client_id": "test_client",
        "response_type": "code",
        "redirect_uri": "http://localhost:8001/",
    }
    # redirect to the identity server login form
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")
    # as a result after making POST request to /authorize endpoint
    # we'll be redirected to redirect_uri with a code


@app.get("/")
async def login_callback(code: str):
    # Exchange the auth code for an access token
    token = await client.get_access_token(
        code=code, redirect_uri="http://localhost:8001/"
    )
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    # Use the access token to access the user info endpoint of the identity server
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(USERINFO_URL, headers=headers)
    return {"message": "success", "profile": userinfo_response.json()}


@app.get("/todos")
async def get_todos(
    authorization: Union[str, None] = Header(default=None),
    auth_swagger: Union[str, None] = Header(
        default=None, description="Authorization"
    ),
):
    if authorization:
        access_token = authorization.split(" ")[-1]
    if auth_swagger is not None:
        access_token = auth_swagger
    # verify token
    # ...
    # if token is not valid or user don't have claims/permission raise an exception

    return {"todos": "blabla"}
