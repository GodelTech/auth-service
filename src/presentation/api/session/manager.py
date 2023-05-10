from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.di.providers import provide_async_session_stub
from functools import wraps
from typing import Callable, Any
from src.presentation.admin_api.models.group import *

def session_manager(func:Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def inner(
        session: AsyncSession = Depends(provide_async_session_stub),
        *args:Any, **kwargs:Any
        ) -> Any:
        try:
            result = await func(session=session,*args, **kwargs)
        except:
            await session.rollback()
            raise
        else:
            await session.commit()
            return result
        finally:
            await session.close()

    return inner
    