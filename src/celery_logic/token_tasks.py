from celery import shared_task
from sqlalchemy import delete, exists, insert, select, extract, func
from datetime import datetime
from src.data_access.postgresql.tables import PersistentGrant, BlacklistedToken
from src.celery_logic.celery_main import celery, Session, logger

# @shared_task
# def sync_clear_database():
#     clear_database.apply_async(expires=3600)

@celery.task
def clear_database():
    session = Session()
    result = delete_expired_tokens(session) + delete_expired_blacklisted_tokens(session)
    session.close()
    return f'Total deleted: {result}'

def delete_expired_tokens(session) -> None:
    delete_query = (
        delete(PersistentGrant)
        .where(
            func.trunc(
                func.extract('epoch', datetime.utcnow())# - func.extract('epoch', PersistentGrant.created_at)
            ) >= PersistentGrant.expiration
        )
        .execution_options(synchronize_session=False)
    )

    result = session.execute(delete_query)
    n = result.rowcount
    session.commit()
    logger.info(f"Deleted {n} expired tokens")
    return n


def delete_expired_blacklisted_tokens(session) -> None:
    delete_query = (
        delete(BlacklistedToken)
        .where(
            func.trunc(
                func.extract('epoch', datetime.utcnow())# - func.extract('epoch', BlacklistedToken.created_at)
            ) >= BlacklistedToken.expiration
        )
        .execution_options(synchronize_session=False)
    )

    result = session.execute(delete_query)
    n = result.rowcount
    session.commit()
    logger.info(f"Deleted {n} expired blacklisted tokens")
    return n