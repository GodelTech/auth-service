from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost/is_db"
)
session = scoped_session(sessionmaker(bind=engine))
# session = scoped_session(sessionmaker(engine, expire_on_commit=False, class_=AsyncSession))
