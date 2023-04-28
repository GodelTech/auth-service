from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

class BaseRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

