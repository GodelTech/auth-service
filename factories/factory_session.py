from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.config import get_app_settings

settings = get_app_settings()
# db_url = settings.database_url.replace('asyncpg', 'psycopg2')
db_url = "postgresql+psycopg2://test:test@localhost:5463/test"
# db_url = "postgresql+psycopg2://test:test@docker:5463/test"

engine = create_engine(db_url)
session = scoped_session(sessionmaker(bind=engine))
