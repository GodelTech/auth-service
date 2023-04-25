from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

class BaseRepository:
    def __init__(self, session):
        self.session:AsyncSession = session
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()
    
    async def close(self):
        await self.session.close()

    