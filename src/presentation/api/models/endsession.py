from typing import Optional

from pydantic import BaseModel


class RequestEndSessionModel(BaseModel):
    id_token_hint: str
    post_logout_redirect_uri: Optional[str]
    state: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"
