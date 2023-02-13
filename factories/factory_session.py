from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.dyna_config import DB_URL

print(DB_URL, " DB_URL:::>>>>>>>>>>>>>>>>>>>>>>>>>>>>::::::::::::::::")

db_url = DB_URL.replace("asyncpg", "psycopg2")

engine = create_engine(db_url)
session = scoped_session(sessionmaker(bind=engine))
