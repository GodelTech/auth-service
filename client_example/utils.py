import jwt
import requests
from Crypto.PublicKey.RSA import construct
from jwkest import base64_to_long

# Identity Server endpoints
AUTH_URL = "http://localhost:8000/authorize/"
TOKEN_URL = "http://localhost:8000/token/"
CONFIG_URL = "http://localhost:8000/.well-known/openid-configuration"
JWKS_URL = "http://localhost:8000/.well-known/jwks"
USERINFO_URL = "http://localhost:8000/userinfo/"
INTROSPECTION_URL = "http://localhost:8000/introspection/"
ENDSESSION_URL = "http://localhost:8000/endsession/"


class TokenValidator:
    def __init__(self, jwks_url: str = JWKS_URL) -> None:
        self.jwks_url = jwks_url
        self.algorithms = ["RS256"]

    async def _get_identity_server_public_key(self) -> bytes:
        response = requests.get(self.jwks_url).json()
        n = base64_to_long(response["keys"][-1]["n"])
        e = base64_to_long(response["keys"][-1]["e"])
        public_key = construct((n, e)).public_key().export_key("PEM")
        return public_key

    async def decode_token(self, token: str, **kwargs) -> dict:
        public_key = await self._get_identity_server_public_key()
        token = token.replace("Bearer ", "")
        decoded_token = jwt.decode(
            token, public_key, algorithms=self.algorithms, **kwargs
        )
        return decoded_token

    async def is_token_valid(self, token: str) -> bool:
        return bool(await self.decode_token(token))


# TODO
# interact with administation/get_users -> how to get access token there
# get users data from the endpoint above
# store data in db
# ! it needs to be done with celery, so the broker is also needed (create docker-compose?)
