from typing import Union, Optional, Any
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import Form
from datetime import date
from pydantic import SecretStr



@dataclass
class RequestUserModel:
    username: str = Form(...)
    email: str  = Form(...)
    password: str  = Form(...)
    name: Optional[str] = Form(None)
    given_name: Optional[str]  = Form(None)
    family_name: Optional[str] = Form(None)
    middle_name: Optional[str] = Form(None)
    preferred_username: Optional[str] = Form(None)
    profile: Optional[str] = Form(None)
    picture: Optional[str] = Form(None)
    website: Optional[str] = Form(None)
    gender: Optional[str] = Form(None)
    birthdate: Optional[date] = Form(None)
    zoneinfo: Optional[str] = Form(None)
    phone_number: Optional[str] = Form(None)
    address: Optional[str] = Form(None)

    class Config:
        orm_mode = True

@dataclass
class RequestAddInfoUserModel:
    name: Optional[str] = Form(None)
    given_name: Optional[str]  = Form(None)
    family_name: Optional[str] = Form(None)
    middle_name: Optional[str] = Form(None)
    last_name: Optional[str] = Form(None)
    preferred_username: Optional[str] = Form(None)
    profile: Optional[str] = Form(None)
    picture: Optional[str] = Form(None)
    website: Optional[str] = Form(None)
    gender: Optional[str] = Form(None)
    birthdate: Optional[date] = Form(None)
    zoneinfo: Optional[str] = Form(None)
    phone_number: Optional[str] = Form(None)
    address: Optional[str] = Form(None)

    class Config:
        orm_mode = True

@dataclass
class RequestLoginModel:
    email: str  = Form(...)
    password: SecretStr  = Form(...)

    class Config:
        orm_mode = True