from sqlalchemy.ext.asyncio import AsyncSession

def session_manager(func):
    async def inner(self, *args, **kwargs):
        try:
            assert isinstance(self.session, AsyncSession) 
            result = await func(self, *args, **kwargs)
        except:
            await self.session.rollback()
            raise
        else:
            await self.session.commit()
        finally:
            await self.session.close()
        return result
    
    return inner