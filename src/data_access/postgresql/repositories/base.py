from sqlalchemy.orm import Session
from fastapi import Depends


class BaseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session
