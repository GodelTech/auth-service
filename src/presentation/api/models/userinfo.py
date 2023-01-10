from typing import Optional
from fastapi import Header
from pydantic import BaseModel

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
