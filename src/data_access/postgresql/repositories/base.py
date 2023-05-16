from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        


