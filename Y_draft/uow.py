from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, engine):
        self.engine = engine

    async def __aenter__(self):
        self.session = AsyncSession(bind=self.engine)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()