from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session
