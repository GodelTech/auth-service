from typing import Optional
from sqlalchemy import JSON, DateTime
from sqlalchemy_utils import ChoiceType
from pydantic import BaseModel

class RequestUserInfoModel(BaseModel):
    authorization: str

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"

class ResponseUserInfoModel(BaseModel):
    sub: str
    name: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    middle_name: Optional[str]
    nickname: Optional[str]
    preferred_username: Optional[str]
    profile: Optional[str]
    picture: Optional[str]
    website: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    gender: Optional[str]
    birthdate: Optional[str]
    zoneinfo: Optional[str]
    locale: Optional[str]
    phone_number: Optional[str]
    phone_number_verified: Optional[bool]
    address: Optional[str]
    updated_at: Optional[int]

    class Config:
        orm_mode = True
