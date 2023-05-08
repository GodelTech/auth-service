import logging

from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import BlacklistedToken


logger = logging.getLogger(__name__)


class BlacklistedTokenRepository():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        token: str,
        expiration: int,
    ) -> None:
        
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            
        blacklisted_token = {
            "token": token,
            "expiration": expiration
        }
            
        await session.execute(
                insert(BlacklistedToken).values(**blacklisted_token)
            )
        await session.commit()
        
    async def exists(
        self,
        token: str, 
    ) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
    
        async with session_factory() as sess:
            session = sess
            
            result = await session.execute(
                select(BlacklistedToken)
                        .where(
                        BlacklistedToken.token == token,
                    )
                )

            result = result.first()
            return bool(result)