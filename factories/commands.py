import factory

import factories.data.data_for_factories as data
import factories.factory_models.client_factory as cl_factory
import factories.factory_models.user_factory as user_factory

factory.random.reseed_random(0)


class DataBasePopulation:
    @classmethod
    def populate_database(cls):
        cls.populate_client_table()
        cls.populate_user_table()
        cls.populate_claims_table()
        cls.populate_client_secrets()

    @classmethod
    def populate_client_table(cls):
        for i in range(len(data.CLIENT_IDS)):
            client = cl_factory.ClientFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_user_table(cls):
        for i in range(len(data.CLIENT_USERNAMES)):
            user = user_factory.UserFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_claims_table(cls):
        for key, val in data.DEFAULT_USER_CLAIMS.items():
            claim = user_factory.UserClaimFactory(
                user_id=1, claim_type=key, claim_value=val
            )
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_client_secrets(cls):
        for item in data.CLIENT_IDS:
            secret = cl_factory.ClientSecretFactory(client_id=item)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()


if __name__ == "__main__":
    DataBasePopulation.populate_database()
