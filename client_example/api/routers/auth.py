import logging
import secrets

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from jwt import PyJWTError

from client_example.httpx_oauth.openid import OpenID
from client_example.utils import CONFIG_URL, TokenValidator

client = OpenID(
    client_id="test_client",
    client_secret="past",
    openid_configuration_endpoint=CONFIG_URL,
)
router = APIRouter(tags=["Authentication"])

logger = logging.getLogger("example_app")


@router.get("/")
async def index(request: Request):
    # TODO add it to middleware <-------------------------------
    token = request.headers.get("Authorization")
    try:
        if token and await TokenValidator().is_token_valid(token):
            return RedirectResponse("/notes")
    except PyJWTError as e:
        logger.exception(e)
    return RedirectResponse("/login")


@router.get("/login")
async def get_login_form(request: Request):
    state = secrets.token_urlsafe(16)
    request.session['state'] = state
    token = request.headers.get("Authorization")
    # TODO add it to middleware <---------------------------------
    try:
        if token and await TokenValidator().is_token_valid(token):
            return RedirectResponse("/notes")
    except PyJWTError as e:
        logger.exception(e)
    auth_url = await client.get_authorization_url(
        redirect_uri="http://localhost:8001/login-callback",
        state=state,
    )
    return RedirectResponse(auth_url)


@router.get("/login-callback")
async def login_callback(code: str, request: Request):
    # Exchange auth code for an access token
    if request.session.get('state') != request.query_params.get('state'):
        return {'error': 'Invalid state'}
    token = await client.get_access_token(
        code=code, redirect_uri="http://localhost:8001/login-callback"
    )
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    print(access_token)
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    return RedirectResponse('/notes')


@router.get("/logout")
async def logout(request: Request):
    token = request.session['access_token']
    response = await client.logout(
        id_token_hint=token, redirect_uri="http://localhost:8001/"
    )
    request.session.clear()
    return RedirectResponse(response.headers['location'])
