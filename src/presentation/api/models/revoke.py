from dataclasses import dataclass
from fastapi import Form
from pydantic import BaseModel


@dataclass
class BodyRequestRevokeModel:
    token: str = Form(...)
    token_type_hint: str = Form(None)

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"  # pragma: no coverage
