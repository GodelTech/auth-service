from sqlalchemy import text
import factories.factory_session as sess
import logging

logger = logging.getLogger(__name__)

class DataBasePurge:

    @classmethod
    def drop_database(cls) -> None:
        try:
            result = sess.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            table_names = [row[0] for row in result]
            excluded_table = 'alembic_version'
            for table_name in table_names:
                if table_name != excluded_table:
                    sess.session.execute(text(f"DROP TABLE {table_name} CASCADE"))
            sess.session.execute(text("TRUNCATE TABLE alembic_version"))
            sess.session.commit()
        except:
            logger.warning("Purge doesn't work")



if __name__ == "__main__":
    DataBasePurge.drop_database()
