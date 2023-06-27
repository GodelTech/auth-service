# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.engine import Engine
# from sqlalchemy.orm import Session
#
# from src.di.providers import provide_db_sync_engine
# from dyna_config import DB_URL, DB_MAX_CONNECTION_COUNT
# def provide_sync_session_stub() -> None:
#     ...
#
#
# def provide_sync_session() -> sessionmaker:
#     engine = provide_db_sync_engine(database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT)
#     sync_session = sessionmaker(engine) #, expire_on_commit=False, class_=Session)
#     return sync_session
