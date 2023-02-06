from urllib.parse import urlencode

import requests
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

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
INTROSPECTION_URL = "http://localhost:8000/introspection/"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='http://localhost:8000/token')


def verify_access_token(token: str, credentials_exception):
    headers = {
        'authorization': f'Bearer {token}',
    }
    response = requests.get(USERINFO_URL, headers=headers)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise credentials_exception
    return response.json()


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)


# ! Probably not implemented in /introspection
async def is_token_valid(token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {"token": token, "token_type_hint": "refresh_token"}
    response = requests.post(INTROSPECTION_URL, headers=headers, data=params)
    return response.json()


@app.get("/login")
async def get_login_form(request: Request):
    token = request.headers.get('Authorization')
    if token and await is_token_valid(token.split(" ")[-1]):
        return RedirectResponse("http://localhost:8001/elo")

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
    # TODO store it on the client side
    # 1. send token to frontend and store it
    # Each time we receive token in a header we need to verify it
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    # Use the access token to access the user info endpoint of the identity server
    print(access_token)
    print()
    print(refresh_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(USERINFO_URL, headers=headers)
    return {"message": "success", "profile": userinfo_response.json()}


@app.get("/todos")
async def get_todos(user: dict = Depends(get_current_user)):
    print(user.get('sub'))
    return {"todos": "blabla"}


# ! to check if token is valid we can go to the /introspect endpoint


# Check if token is valid
# Try to refresh it?
# pass again
