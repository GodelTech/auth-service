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


class TokenValidator:
    def __init__(self, jwks_url: str = JWKS_URL) -> None:
        self.jwks_url = jwks_url
        self.algorithms = ["RS256"]

    async def _get_identity_server_public_key(self) -> bytes:
        response = requests.get(self.jwks_url).json()
        n = base64_to_long(response["keys"][-1]["n"])
        e = base64_to_long(response["keys"][-1]["e"])
        public_key = construct((n, e)).public_key().export_key('PEM')
        return public_key

    async def is_token_valid(self, token: str) -> bool:
        public_key = await self._get_identity_server_public_key()
        token = token.replace("Bearer ", "")

        try:
            jwt.decode(token, public_key, algorithms=self.algorithms)
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
