from datetime import datetime
from typing import Union

from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    content: Union[str, None] = None


class RequestNoteCreate(NoteBase):
    pass


class ResponseNote(NoteBase):
    id: int
    created_at: datetime
    user_id: int
    # user: ResponseUser

    class Config:
        orm_mode = True
