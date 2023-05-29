import factory
from sqlalchemy import text

import factories.data.data_for_factories as data
import factories.factory_models.client_factory as cl_factory
import factories.factory_models.user_factory as user_factory
import factories.factory_session as sess


factory.random.reseed_random(0)


class DataBasePurge:
    @classmethod
    def populate_database(cls) -> None:
        # clean data from the tables in database
        cls.clean_data_from_database()

    @classmethod
    def clean_data_from_database(cls) -> None:
        result = sess.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        table_names = [row[0] for row in result]
        excluded_table = 'alembic_version'
        for table_name in table_names:
            if table_name != excluded_table:
                sess.session.execute(text(f"DROP TABLE {table_name} CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE alembic_version"))
        sess.session.commit()



if __name__ == "__main__":
    DataBasePurge.populate_database()
