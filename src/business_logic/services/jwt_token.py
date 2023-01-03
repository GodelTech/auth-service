import datetime
import logging

import jwt

logger = logging.getLogger("is_app")

SECRET = "123"


class JWTService:
    """Service for: encoding dictionaries into JWT; decoding JWT; setting and checking time boarders of token"""

    """
    to decode:
        JWTService.decode_token(token = "your JWT")

    to encode:
        JWTService.encode_jwt(payload = {your dict to encode}, include_expire = True/False (if you need))

    to set expire time:
        JWTService.expire = your datetime_object (without microseconds(use datetime_object.replace(microsecond=0))

        OR

        JWTService.set_expire_time(expire_days: int , expire_hours: int , expire_minutes: int , expire_seconds: int )

        !!! Defoultly all parameters are 0. At least one parameter has to be > 0, and all parameters have to be positive !!!

    to check if token is spoiled:
        JWTService.check_spoiled_token(token =your_token)

        Function returns "True" if token is expired
        !!! Time has to be in format '%Y-%m-%d %H:%M:%S' !!!
    """

    def __init__(
        self, algorithm: str = "HS256", algorithms: list = ["HS256"]
    ) -> None:
        self.secret = SECRET
        self.algorithm = algorithm
        self.algorithms = algorithms

    def check_spoiled_token(self, token: str):
        token_date = datetime.datetime.strptime(
            self.decode_token(token)["expire"], "%Y-%m-%d %H:%M:%S"
        )
        return self.get_datetime_now() > token_date

    def set_expire_time(
        self,
        expire_days: int = 0,
        expire_hours: int = 0,
        expire_minutes: int = 0,
        expire_seconds: int = 0,
    ) -> datetime.datetime:

        for num in (expire_days, expire_hours, expire_minutes, expire_seconds):
            if num < -0:
                raise ValueError
        if (
            sum((expire_days, expire_hours, expire_minutes, expire_seconds))
            == 0
        ):
            raise ValueError

        date_expire = self.get_datetime_now()
        time_delt = datetime.timedelta(
            days=expire_days,
            hours=expire_hours,
            minutes=expire_minutes,
            seconds=expire_seconds,
        )
        self.expire = date_expire + time_delt

    def get_datetime_now(self):
        return datetime.datetime.now().replace(microsecond=0)

    def encode_jwt(
        self, payload: dict = {}, include_expire: bool = True
    ) -> str:

        if include_expire:
            payload = payload | {"expire": str(self.expire)}

        token = jwt.encode(payload, self.secret, self.algorithm)

        if include_expire:
            logger.info(f"Created token. Expires at{self.expire}")
        else:
            logger.info(f"Created token. Will not expire")

        return token

    def decode_token(
        self,
        token: str,
    ) -> dict:
        token = token.replace("Bearer ", "")
        decoded = jwt.decode(token, self.secret, self.algorithms)
        return decoded
