import logging

from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import BlacklistedToken


logger = logging.getLogger(__name__)


class BlacklistedTokenRepository(BaseRepository):

    async def create(
        self,
        token: str,
        expiration: int,
    ) -> None:
        
        blacklisted_token = {
            "token": token,
            "expiration": expiration
        }
            
        await self.session.execute(
                insert(BlacklistedToken).values(**blacklisted_token)
            )
        await self.session.commit()
        
    async def exists(
        self,
        token: str, 
    ) -> bool:    
        result = await self.session.execute(
            select(BlacklistedToken)
                    .where(
                    BlacklistedToken.token == token,
                )
            )

        result = result.first()
        return bool(result)