import json
from datetime import datetime

import jwt
import requests
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from db import StubDatabase

# Configuration
config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name="oidc_provider",
    server_metadata_url="http://localhost:8000/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile", "response_type": "id_token token"},
    # the below line is here because our auth server
    # doesn't accept client_id and client_secret in the Authorization header
    access_token_params={"client_id": "spider_man"},
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret")
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pseudo_db = StubDatabase()


def read_file_content(file_path: str) -> str:
    with open(file_path, "r") as file:
        content = file.read()
    return content


def decode_id_token(id_token: str) -> dict:
    """
    Decodes the id token using the provided key and returns its payload as a dictionary.
    """
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    return decoded


async def get_user(request: Request):
    """
    Returns the user stored in the request session.
    Example of returned value (real example):
    {
        "iss": "http://127.0.0.1:8000",
        "client_id": "spider_man",
        "iat": 1686583702,
        "exp": 1686584302,
        "sub": 8,
        "aud": [
            "spider_man"
        ],
        "nonce": "pPMg5fxJyeqHY3IxHeWA"
    }
    """
    return request.session.get("user")


@app.get("/")
async def homepage(request: Request, user=Depends(get_user)):
    if user:
        str_expiration = datetime.fromtimestamp(user["exp"]).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
        content = read_file_content("html/authorized-page.html")
        content = content.replace(
            "{{{str_expiration_variable}}}", str_expiration
        ).replace("{{{user_info_variable}}}", json.dumps(user, indent=4))
        return HTMLResponse(content=content)
    else:
        content = read_file_content("html/unauthorized-page.html")
        return HTMLResponse(content=content)


@app.get("/userinfo")
async def userinfo(request: Request):
    server_metadata = await oauth.oidc_provider.load_server_metadata()
    userinfo_endpoint = server_metadata.get("userinfo_endpoint")

    auth_data = pseudo_db.get("auth_data")
    if not auth_data:
        pseudo_db.delete("auth_data")
        request.session.clear()
        return RedirectResponse(url="/")
    breakpoint()
    access_token = auth_data["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(userinfo_endpoint, headers=headers)
    content = read_file_content("html/userinfo-page.html").replace(
        "{{{user_info_variable}}}", json.dumps(response.json(), indent=4)
    )
    return HTMLResponse(content=content)


@app.get("/login")
async def login(request: Request):
    redirect_uri = str(request.url_for("auth"))
    return await oauth.oidc_provider.authorize_redirect(request, redirect_uri, response_mode='fragment')


@app.get("/logout")
async def logout(request: Request):
    server_metadata = await oauth.oidc_provider.load_server_metadata()
    end_session_endpoint = server_metadata.get("end_session_endpoint")

    active_auth_data = pseudo_db.get("auth_data")

    if not active_auth_data:
        request.session.clear()
        return RedirectResponse(url="/")

    id_token_hint = active_auth_data["id_token"]
    post_logout_redirect_uri = str(request.url_for("endsession"))

    return RedirectResponse(
        url=end_session_endpoint
            + "?id_token_hint="
            + id_token_hint
            + "&post_logout_redirect_uri="
            + post_logout_redirect_uri
    )


@app.get("/endsession")
async def endsession(request: Request):
    pseudo_db.delete("auth_data")
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/auth")
async def auth(request: Request):
    # auth_data = await oauth.oidc_provider.authorize_access_token(request)
    # Auth data is like (real example):
    # {
    #     "access_token": "ACCESS_TOKEN",
    #     "refresh_token": "REFRESH_TOKEN",
    #     "id_token": "ID_TOKEN",
    #     "expires_in": 600,
    #     "token_type": "Bearer",
    #     "expires_at": 1686584302,
    #     "userinfo": {
    #         "iss": "ISSUER",
    #         "client_id": "CLIENT_ID",
    #         "iat": 1686583702,
    #         "exp": 1686584302,
    #         "sub": 8,
    #         "aud": [
    #             "CLIENT_ID"
    #         ],
    #         "nonce": "NONCE"
    #     }
    # }
    breakpoint()
    id_token_string = request.query_params.get('id_token')
    access_token_string = request.query_params.get('access_token')
    if id_token_string:
        userinfo = decode_id_token(id_token_string)
        request.session["user"] = userinfo
        pseudo_db.set_or_overwrite('auth_data', {'userinfo': userinfo,
                                                 'id_token': id_token_string,
                                                 'access_token': access_token_string,
                                                 })
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
