from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from src.config import get_app_settings

settings = get_app_settings()
db_url = settings.database_url.replace('asyncpg', 'psycopg2')
engine = create_engine(
    db_url
)
session = scoped_session(sessionmaker(bind=engine))
