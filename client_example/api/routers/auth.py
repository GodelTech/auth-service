import logging

from fastapi import APIRouter, Request, Response, status
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
    # TODO add it to middleware maybe
    token = request.headers.get("Authorization")
    try:
        if token and await TokenValidator().is_token_valid(token):
            return RedirectResponse("/notes")
    except PyJWTError as e:
        logger.exception(e)
    return RedirectResponse("/login")


@router.get("/login")
async def get_login_form(request: Request):
    token = request.headers.get("Authorization")
    try:
        if token and await TokenValidator().is_token_valid(token):
            return RedirectResponse("/notes")
    except PyJWTError as e:
        logger.exception(e)
    auth_url = await client.get_authorization_url(
        redirect_uri="http://localhost:8001/login-callback"
    )
    return RedirectResponse(auth_url)


@router.get("/login-callback")
async def login_callback(code: str):
    # Exchange the auth code for an access token
    token = await client.get_access_token(
        code=code, redirect_uri="http://localhost:8001/login-callback"
    )
    # TODO store it on the client side
    # Store both tokens on client side localStorage
    access_token, refresh_token = token["access_token"], token["refresh_token"]
    response = RedirectResponse('/test')
    response.set_cookie(
        key='access_token',
        value=access_token,
        domain='localhost',
        path='/',
    )
    return response


@router.get("/test2")
async def test2():
    response = RedirectResponse('/test')
    response.set_cookie(
        'with_samesite2',
        'test',
        domain='localhost',
        path='/',
    )
    return response


@router.get("/test")
async def test(request: Request):
    test_cookie = request.cookies.get('access_token')
    if test_cookie:
        return {
            "message": f"The value of the 'test' cookie is '{test_cookie}'."
        }
    return {"message": "The 'test' cookie is not set."}


@router.get("/logout")
async def logout(request: Request):
    token = request.headers['Authorization']
    response = await client.logout(
        id_token_hint=token, redirect_uri="http://localhost:8001/"
    )
    return RedirectResponse(response.headers['location'])
