import logging
import secrets

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from client_example.httpx_oauth.openid import OpenID
from client_example.utils import CONFIG_URL

client = OpenID(
    client_id="test_client",
    client_secret="past",
    openid_configuration_endpoint=CONFIG_URL,
)
router = APIRouter(tags=["Authentication"])

logger = logging.getLogger("example_app")


@router.get("/")
async def index():
    return RedirectResponse("/login")


@router.get("/login")
async def get_login_form(request: Request):
    state = secrets.token_urlsafe(16)
    request.session["state"] = state
    auth_url = await client.get_authorization_url(
        redirect_uri="http://localhost:8001/login-callback",
        state=state,
    )
    return RedirectResponse(auth_url)


@router.get("/login-callback")
async def login_callback(code: str, request: Request):
    # Exchange auth code for an access token
    if request.session.get("state") != request.query_params.get("state"):
        return {"error": "Invalid state"}

    token = await client.get_access_token(
        code=code, redirect_uri="http://localhost:8001/login-callback"
    )
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    response = RedirectResponse("/notes")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        domain=request.url.hostname,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        domain=request.url.hostname,
        path="/",
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    access_token = request.headers.get("access_token")
    await client.revoke_token(
        token=access_token, token_type_hint="access_token"
    )
    response = await client.logout(
        id_token_hint=access_token, redirect_uri="http://localhost:8001/"
    )
    request.session.clear()
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
