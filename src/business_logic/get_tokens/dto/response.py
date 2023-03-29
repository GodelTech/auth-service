from pydantic import BaseModel
from typing import Optional, Union


class ResponseTokenModel(BaseModel):

    access_token: Optional[str]
    token_type: Optional[str]
    refresh_token: Optional[str]
    expires_in: Optional[int]
    id_token: Optional[str]
    refresh_expires_in : Optional[int]
    not_before_policy : Optional[int]
    scope : Optional[Union[list[str], str]]
    
    class Config:
        orm_mode = True
