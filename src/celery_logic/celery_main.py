from src.dyna_config import (
    DB_URL,
    REDIS_URL,
    CELERY_CLEANER_CRONE,
)
from celery import Celery
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery.schedules import crontab

logger = logging.getLogger(__name__)


sync_db_url = DB_URL.replace('+asyncpg', '')
engine = create_engine(sync_db_url)
Session = sessionmaker(bind=engine)

celery = Celery(
    "celery_tasks", 
    broker=REDIS_URL, 
    backend=REDIS_URL, 
    include=['src.celery_logic.token_tasks']
    )

celery.conf.beat_schedule = {
    'execute_task_cron': {
        'task': 'src.celery_logic.token_tasks.clear_database',
        'schedule': CELERY_CLEANER_CRONE,
    },
}




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