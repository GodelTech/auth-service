from sqlalchemy.ext.asyncio import AsyncEngine


class BaseRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> AsyncEngine:
        return self._engine
