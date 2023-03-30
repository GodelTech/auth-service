from typing import Union, Optional, Any
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import Form
from datetime import date

@dataclass
class RequestUserModel:

    username: str = Form(...)
    email: str  = Form(...)
    password: str  = Form(...)
    
    name: str  = Form(...)
    given_name: Optional[str]  = Form(None)
    family_name: Optional[str] = Form(None)
    middle_name: Optional[str] = Form(None)
    preferred_username: Optional[str] = Form(None)
    profile: Optional[str] = Form(None)
    picture: Optional[str] = Form(None)
    website: Optional[str] = Form(None)
    
    gender: str = Form(...)
    birthdate: date = Form(...)
    zoneinfo: Optional[str] = Form(None)
    phone_number: str = Form(...)
    address: str = Form(...)


    class Config:
        orm_mode = True
