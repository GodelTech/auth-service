import jwt

SECRET = "123"


class JWTService():
    def __init__(self, algorithm: str = "HS256", algorithms: list = ["HS256"]) -> None:
        self.secret = SECRET
        self.algorithm = algorithm
        self.algorithms = algorithms

    def encode_jwt(self, payload: dict = {"sub": "1", "name": "Danya"}) -> str:
        token = jwt.encode(payload, self.secret, self.algorithm)
        return token

    def decode_token(self, token: str,) -> dict:
        token = token.replace("Bearer ", '')
        decoded = jwt.decode(token, self.secret, self.algorithms)
        return decoded
