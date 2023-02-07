import jwt
import requests
from Crypto.PublicKey.RSA import construct
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwkest import base64_to_long

# Identity Server endpoints
AUTH_URL = "http://localhost:8000/authorize/"
TOKEN_URL = "http://localhost:8000/token/"
JWKS_URL = "http://localhost:8000/.well-known/jwks"
USERINFO_URL = "http://localhost:8000/userinfo/"
INTROSPECTION_URL = "http://localhost:8000/introspection/"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


def get_identity_server_public_key():
    response = requests.get(JWKS_URL).json()
    n = base64_to_long(response["keys"][-1]["n"])
    e = base64_to_long(response["keys"][-1]["e"])
    public_key = construct((n, e)).public_key().export_key('PEM')
    return public_key


async def is_token_valid_test(token):
    public_key = get_identity_server_public_key()
    token = token.replace("Bearer ", "")
    try:
        jwt.decode(token, public_key, algorithms=["RS256"])
        return True
    except (
        jwt.exceptions.InvalidSignatureError,
        jwt.exceptions.DecodeError,
        jwt.exceptions.ExpiredSignatureError,
    ) as e:
        print(e)
        # if expired refresh token
        return False


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


def get_access_token_from_header(request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        bearer, token = authorization.split(" ")
        if bearer != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


async def auth_middleware(request, call_next):
    try:
        access_token = get_access_token_from_header(request)
        is_valid = await is_token_valid_test(access_token)
        if is_valid:
            response = await call_next(request)
            return response
        else:
            raise HTTPException(status_code=400, detail="Not authenticated")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Not authenticated")
