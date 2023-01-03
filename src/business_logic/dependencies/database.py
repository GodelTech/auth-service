from typing import Callable, Type

from fastapi import Depends
from sqlalchemy.orm import Session

from src.data_access.postgresql.repositories.base import BaseRepository
from src.di import Container


def get_repository(
    repo_type: Type[BaseRepository],
) -> Callable[[Session], BaseRepository]:
    def _get_repo(
        session: Session = Depends(Container.db().get_connection),
    ) -> BaseRepository:
        return repo_type(session)

    return _get_repo
