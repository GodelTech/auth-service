import requests
from fastapi import FastAPI, HTTPException, status
from httpx import AsyncClient

app = FastAPI()

# Identity Server endpoint
AUTH_SERVER = "http://localhost:8000"
AUTH_URL = "http://localhost:8000/authorize/"
TOKEN_URL = "http://localhost:8000/token/"
USERINFO_URL = "http://localhost:8000/userinfo/"


@app.get("/login")
async def login():
    # Get the authorization code by redirecting the user to the authorization endpoint of the identity server
    # Check if user is auth
    # If auth: redirect to profile
    # If not auth: Some kind of form opens -> we provide username and password and both values goes to the scope?
    authorization_endpoint = "http://localhost:8000/authorize/"
    client_id = "test_client"
    redirect_uri = "http://localhost:8001/profile"
    response_type = "code"
    scope = f"gcp-api%2520IdentityServerApi%26grant_type%3Dpassword%26client_id%3Dtest_client%26client_secret%3D65015c5e-c865-d3d4-3ba1-3abcb4e65500%26password%3Dtest_password%26username%3DTestClient"
    state = "state"

    authorization_url = f"{authorization_endpoint}?client_id={client_id}&response_type={response_type}&scope={scope}&redirect_uri={redirect_uri}&state={state}"
    # redirection to identity server login page or smth
    raise HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={"location": authorization_url},
    )


@app.get("/profile")
async def profile(code: str):
    access_token = await obtain_jwt(code)

    # Use the access token to access the user info endpoint of the identity server
    headers = {"Authorization": access_token}
    userinfo_response = requests.get(USERINFO_URL, headers=headers)
    return userinfo_response.json()


async def obtain_jwt(auth_code: str) -> str:
    data = {
        "client_id": "test_client",
        "grant_type": "code",
        "scope": "test",
        "redirect_uri": "https://www.google.com/",
        "code": auth_code,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = await AsyncClient().request(
        'POST', f'{AUTH_SERVER}/token/', data=data, headers=headers
    )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code",
        )
    return response.json().get('access_token')


# grant_type: code
#   - redirect_uri, code
# grant_type: password
#   - username, password
# grant_type: refresh_token
#   - refresh_token
# grant_type: urn:ietf:params:oauth:grant-type:device_code
#   - device_code


# implement it for different grant_types?


# @app.get("/protected")
# async def protected(access_token: str):
#     # check if token was created by identity server?
#     # check if token is valid?
#     headers = {"authorization": access_token}
#     response = await AsyncClient().request(
#         'GET', "http://localhost:8001/protected", headers=headers
#     )
#     return response.json()


# @app.post("/auth_code")
# async def auth_code(auth_code: str):
#     try:
#         access_token = await obtain_jwt(auth_code)
#     except HTTPException as e:
#         return {"message": str(e.detail)}
#     return {"access_token": access_token}
