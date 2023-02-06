from typing import List
from urllib.parse import urlencode

import requests
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db
from .httpx_oauth.openid import OpenID
from .schemas import ResponseNote

client = OpenID(
    client_id="test_client",
    client_secret="past",
    openid_configuration_endpoint="http://localhost:8000/.well-known/openid-configuration",
)

models.Base.metadata.create_all(bind=engine)

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


async def is_token_valid(token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {"token": token, "token_type_hint": "refresh_token"}
    response = requests.post(INTROSPECTION_URL, headers=headers, data=params)
    return response.json()


@app.get("/")
async def index(request: Request):
    token = request.headers.get('Authorization')
    if token and await is_token_valid(token.split(" ")[-1]):
        return RedirectResponse("/notes")
    else:
        return RedirectResponse("/login")


@app.get("/login")
async def get_login_form(request: Request):
    token = request.headers.get('Authorization')
    if token and await is_token_valid(token.split(" ")[-1]):
        return RedirectResponse("/notes")

    params = {
        "client_id": "test_client",
        "response_type": "code",
        "redirect_uri": "http://localhost:8001/login-callback",
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@app.get("/login-callback")
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
    return RedirectResponse("/notes")


@app.get("/notes", response_model=List[ResponseNote])
async def get_notes(
    limit: int = 10,
    skip: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = crud.get_notes(db, skip, limit)
    if notes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have any notes.",
        )

    return notes


@app.get("/notes/{id}", response_model=schemas.ResponseNote)
async def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    note = crud.get_note(db, id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found.",
        )
    if note.user_id != int(current_user['sub']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action.",
        )
    return note


@app.post("/notes", status_code=status.HTTP_201_CREATED)
async def create_notes(
    request_body: schemas.RequestNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud.create_user_note(
        db=db, item=request_body, user_id=current_user['sub']
    )
