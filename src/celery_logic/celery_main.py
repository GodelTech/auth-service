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
