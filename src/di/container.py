from dependency_injector import containers, providers

from src.config import get_app_settings
from src.data_access.postgresql import Database
from src.business_logic.services.admin_api import AdminUserService
from src.data_access.postgresql.repositories import UserRepository, ClientRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


async def get_session(db: Database) -> AsyncSession:
        return await db.get_connection().__anext__()


class Container(containers.DeclarativeContainer):
    config = providers.Object(get_app_settings())

    db:Database = providers.Singleton(
        Database,
        database_url=str(config().database_url),
        max_connection_count=config().max_connection_count,
    )

    async_session = providers.Resource(
        get_session,
        db=db,
    )
    
    user_repo = providers.Factory(
        UserRepository,
        session=async_session,
    )
    client_repo = providers.Factory(
        ClientRepository,
        session=async_session,
    )

    admin_user_service = providers.Factory(
        AdminUserService,
        user_repo=user_repo,
        client_repo=client_repo
    )

  
    