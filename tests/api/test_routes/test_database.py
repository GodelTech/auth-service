import asyncio

import aiosqlite

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.data_access.postgresql.tables.base import Base, BaseModel
from src.data_access.postgresql.tables import identity_resource, persistent_grant, users, resources_related, client
from src.data_access.postgresql.tables.client import Client

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test_async.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
# engine = create_async_engine("sqlite+aiosqlite:///:memory:")

# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)


# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#
# asyncio.run(init_models())
