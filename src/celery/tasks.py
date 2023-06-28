# from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.dyna_config import (
    DB_MAX_CONNECTION_COUNT,
    DB_URL,
    REDIS_URL,
)
# import src.di.providers as prov
from celery import shared_task, Celery
from asgiref.sync import async_to_sync
import os
from sqlalchemy import delete, exists, insert, select, extract, func
from datetime import datetime
from src.data_access.postgresql.tables import PersistentGrant, Client
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)



celery = Celery('worker')
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379")
sync_db_url = "postgresql://postgres:postgres@localhost:5432/is_db"
engine = create_engine(sync_db_url)
Session = sessionmaker(bind=engine)

celery = Celery("celery_tasks", broker=REDIS_URL, backend=REDIS_URL)

@shared_task
def sync_clear_database():
    clear_database.apply_async(countdown =5)

@celery.task
def clear_database():
    # print('a')
    
    session = Session()
    # print(session)
    # print(engine)
    delete_expired_tokens(session)
    session.commit()
    #next_time = round(get_next_cleaning_time(session), 2)
    session.close()
    next_time = 5
    logger.info(f"Next cleaning in {next_time}.")
    clear_database.apply_async(countdown=next_time)


def delete_expired_tokens(session) -> None:
    delete_query = (
        delete(PersistentGrant)
        .where(
            func.trunc(
                func.extract('epoch', datetime.utcnow()) - func.extract('epoch', PersistentGrant.created_at)
            ) >= PersistentGrant.expiration
        )
        .execution_options(synchronize_session=False)
    )

    session.execute(delete_query)
    session.commit()
    logger.info(f"Deleted expired tokens")


# def get_next_cleaning_time(session) -> float:
#     # min_value = session.query(func.min(func.extract('epoch', PersistentGrant.created_at)) + PersistentGrant.expiration).scalar()
#     # print(min_value)
#     # if check_not_empty(session):
#         # query = select(func.min(extract('epoch', PersistentGrant.created_at) ) + PersistentGrant.expiration)
#         # result = session.execute(query)
#     min_value = session.query(
#         func.coalesce(func.min(func.extract('epoch', PersistentGrant.created_at) + PersistentGrant.expiration), 0)
#     ).scalar()
#     min_value_token = float(min_value) - datetime.utcnow().timestamp()

#     result = session.execute(select(func.min(Client.absolute_refresh_token_lifetime)))
#     min_value = result.scalar()
#     return min_value

# def check_not_empty(session):
#     query = select(exists().where(PersistentGrant.id!=None))
#     result = session.execute(query)
#     print(result)
#     return result.scalar()