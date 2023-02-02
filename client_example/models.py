from dataclasses import dataclass
from typing import Optional

from fastapi import Form


@dataclass
class BodyRequestLoginModel:
    username: str = Form(...)
    password: str = Form(...)

    class Config:
        orm_mode = True
