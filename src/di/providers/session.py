from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def provide_sync_session_stub() -> None:
    ...


def provide_sync_session(engine: Engine) -> sessionmaker:
    sync_session = sessionmaker(engine) #, expire_on_commit=False, class_=Session)
    return sync_session
