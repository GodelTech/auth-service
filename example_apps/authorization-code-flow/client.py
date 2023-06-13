from datetime import datetime
import json

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt
import requests
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from db import StubDatabase
from fastapi import Depends


# Configuration
config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name="oidc_provider",
    server_metadata_url="http://localhost:8000/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
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
    Example of returned value:
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
    return await oauth.oidc_provider.authorize_redirect(request, redirect_uri)


@app.get("/refresh")
async def refresh(request: Request):
    auth_data = pseudo_db.get("auth_data")

    if not auth_data:
        return RedirectResponse(url="/")

    refresh_token = auth_data["refresh_token"]

    new_auth_data = await oauth.oidc_provider.fetch_access_token(
        grant_type="refresh_token",
        refresh_token=refresh_token,
    )

    id_token = new_auth_data["id_token"]
    userinfo = decode_id_token(id_token)

    auth_data = {**new_auth_data, "userinfo": userinfo}

    pseudo_db.set_or_overwrite("auth_data", auth_data)

    request.session["user"] = userinfo

    return RedirectResponse(url="/")


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
    auth_data = await oauth.oidc_provider.authorize_access_token(request)
    # Auth data is like:
    # {
    #     "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAiLCJjbGllbnRfaWQiOiJzcGlkZXJfbWFuIiwiaWF0IjoxNjg2NTgzNzAyLCJleHAiOjE2ODY1ODczMDIsInN1YiI6OCwic2NvcGUiOm51bGwsImF1ZCI6WyJpbnRyb3NwZWN0aW9uIiwicmV2b2NhdGlvbiIsInVzZXJpbmZvIl19.VvD0oSQVXbVmT1dz8qLAyK7dGcXcfW6D_TZ26FQ5m5vvufgySF7ZgEv5MiwC-H-aOaTdD0zmypNRjait1cFzthAJ8XsjPpiJwJPGt-L1O9-XErDVLqfewjoi3rWQy4wYo8mM39De0l5FlOMJMnicvN-6jp10PB27ICVY3t13C8VyTsUbuXhWgKuF7K3wb17NOZhiff-zZLnVUtR90JW1g1IFJ_r14TK4gKWOidhL4pp--LsFjjt8JIAlLrfLlSvaVsEg6Wb7TZh6NLXmiN2BhjoDMIOJe-KydHqGpzu0hyJEayCDC-DRWJGky9rfHuLGEXTDkc2l0kjdl7yU3_NRPg",
    #     "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAiLCJjbGllbnRfaWQiOiJzcGlkZXJfbWFuIiwiaWF0IjoxNjg2NTgzNzAyLCJleHAiOjE2ODY1ODczMDIsInN1YiI6OCwic2NvcGUiOm51bGwsImF1ZCI6WyJzcGlkZXJfbWFuIl19.GhaKbtk3PJuL8dlTYCFp0UGf7pFv-a05OzZTddp9WqjiufQ0DA41T7nq5nyw4O9i5tny7JrLWEjFXsMD2EtR_7czlrPCUwk9J2e4glzREpgUzj0FnAL-bybUJZ1ED5S8py0vxQd4qlGwVbevCQjoqP_zqMurpHAsG5WWQ8f4Z_-nHVssWlrQwn8K88QeNLhn87I0PhlZApbn-bw3VWOYeP09hlV6BcWRwgQxzl8ifmedhcktMEqRLAsrSUAYc-2oRDG71G7Wh0j-ioGbga6HiUzQPRBD0ByFsODQ_OfYoeVXG82Qlb4N9DkKk6AME4q2s2qfeTmdeyYWYMB-O7w5vw",
    #     "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAiLCJjbGllbnRfaWQiOiJzcGlkZXJfbWFuIiwiaWF0IjoxNjg2NTgzNzAyLCJleHAiOjE2ODY1ODQzMDIsInN1YiI6OCwiYXVkIjpbInNwaWRlcl9tYW4iXX0.MSbIPqMNepZIZnh_Njx2uAkXP-A1prEBwqnwtr81YBCj-fcVc9hr7QlYSjVryJMep9zfypVzLVMy-qWNTQAocp8nL0HKMjRDJYtUWl4p8D7tFGpMv2Y9TBFpaT9GReaZa3JGMJ0uW2Yev6EE8aUajbzOqPkwQC-lohh_AbpxZBMyJG80jnI8aFyv3DHgRgndEaxqIYTUFJxsxPiwacLUAs3IMw1vS0P33UeExeg3BLJGixp0NTCmc8dEULt7gu0Kvm8h5ArDf7b5AQYl9ZiAC8ml15yf5YC_oFPHZtbbWn78S7_kN2PZ2StOndgLdtdl4P_S692t2gpt-PlqI6qZrw",
    #     "expires_in": 600,
    #     "token_type": "Bearer",
    #     "expires_at": 1686584302,
    #     "userinfo": {
    #         "iss": "http://127.0.0.1:8000",
    #         "client_id": "spider_man",
    #         "iat": 1686583702,
    #         "exp": 1686584302,
    #         "sub": 8,
    #         "aud": [
    #             "spider_man"
    #         ],
    #         "nonce": "pPMg5fxJyeqHY3IxHeWA"
    #     }
    # }
    pseudo_db.set_or_overwrite("auth_data", auth_data)
    request.session["user"] = auth_data["userinfo"]
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
