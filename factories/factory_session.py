from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost/is_db"
)
session = scoped_session(sessionmaker(bind=engine))

DATABASE_ASYNC_URL = "postgresql+asyncpg://postgres:postgres@localhost/is_db"

async_engine = create_async_engine(
    DATABASE_ASYNC_URL,
    echo=True,
    future=True,
)

async_session = scoped_session(sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession))
