from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from client_example.httpx_oauth.openid import OpenID
from client_example.utils import AUTH_URL, TokenValidator

client = OpenID(
    client_id="test_client",
    client_secret="past",
    openid_configuration_endpoint="http://localhost:8000/.well-known/openid-configuration",
)
router = APIRouter(tags=['Authentication'])


@router.get("/")
async def index(request: Request):
    token = request.headers.get('Authorization')
    if token and await TokenValidator().is_token_valid(token):
        return RedirectResponse("/notes")
    else:
        return RedirectResponse("/login")


@router.get("/login")
async def get_login_form(request: Request):
    token = request.headers.get('Authorization')
    if token and await TokenValidator().is_token_valid(token):
        return RedirectResponse("/notes")

    params = {
        "client_id": "test_client",
        "response_type": "code",
        "redirect_uri": "http://localhost:8001/login-callback",
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@router.get("/login-callback")
async def login_callback(code: str):
    # Exchange the auth code for an access token
    token = await client.get_access_token(
        code=code, redirect_uri="http://localhost:8001/"
    )
    # TODO store it on the client side
    # 1. send token to frontend and store it
    # Each time we receive token in a header we need to verify it
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    print(access_token)
    # public_key = get_identity_server_public_key()
    # if not is_token_valid(access_token, public_key):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    # Use the access token to access the user info endpoint of the identity server
    return RedirectResponse("/notes")
