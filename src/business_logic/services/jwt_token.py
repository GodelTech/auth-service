import jwt
import datetime
import logging

logger = logging.getLogger('is_app')

SECRET = "123"


class JWTService():
    def __init__(self, algorithm: str = "HS256", algorithms: list = ["HS256"], expire_days: int = 0, expire_hours: int = 0, expire_minutes: int = 0, expire_seconds: int = 0) -> None:
        self.secret = SECRET
        self.algorithm = algorithm
        self.algorithms = algorithms
        

    def check_spoiled_token(self, token):
        token_date = datetime.datetime.strptime(self.decode_token(token)["expire"], '%Y-%m-%d %H:%M:%S')
        return datetime.datetime.now() >= token_date

    def set_expire_time(self, expire_days: int = 0, expire_hours: int = 0, expire_minutes: int = 0, expire_seconds: int = 0) -> datetime.datetime:

        for num in (expire_days, expire_hours, expire_minutes, expire_seconds):
            if num < -0:
                raise ValueError
        if sum((expire_days, expire_hours, expire_minutes, expire_seconds)) == 0:
            raise ValueError

        date_expire = datetime.datetime.now().replace(microsecond=0)
        time_delt = datetime.timedelta(
            days=expire_days, minutes=expire_minutes, seconds=expire_seconds)
        self.expire = date_expire+time_delt

    def encode_jwt(self, payload: dict = {"sub": "1", "name": "Danya"}) -> str:
        token = jwt.encode(payload | {"expire": str(
            self.expire)}, self.secret, self.algorithm)
        logger.info(f"Created token. Expires at{self.expire}")
        return token

    def decode_token(self, token: str,) -> dict:
        token = token.replace("Bearer ", '')
        decoded = jwt.decode(token, self.secret, self.algorithms)
        return decoded
