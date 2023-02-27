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
        sess.session.execute(text("DROP TABLE api_claim_types CASCADE"))
        sess.session.execute(text("DROP TABLE api_scope_claim_types CASCADE"))
        sess.session.execute(text("DROP TABLE api_secrets_types CASCADE"))
        sess.session.execute(text("DROP TABLE persistent_grant_types CASCADE"))
        sess.session.execute(text("DROP TABLE identity_providers CASCADE"))
        sess.session.execute(text("DROP TABLE identity_providers_mapped CASCADE"))

        sess.session.execute(text("DROP TABLE devices CASCADE"))
        sess.session.execute(text("DROP TABLE access_token_types CASCADE"))
        sess.session.execute(text("DROP TABLE protocol_types CASCADE"))
        sess.session.execute(text("DROP TABLE refresh_token_expiration_types CASCADE"))
        sess.session.execute(text("DROP TABLE refresh_token_usage_types CASCADE"))
        sess.session.execute(text("DROP TABLE user_claim_types CASCADE"))
        sess.session.execute(text("DROP TABLE api_claims CASCADE"))
        sess.session.execute(text("DROP TABLE api_resources CASCADE"))
        sess.session.execute(text("DROP TABLE api_scope_claims CASCADE"))
        sess.session.execute(text("DROP TABLE api_scopes CASCADE"))
        sess.session.execute(text("DROP TABLE api_secrets CASCADE"))
        sess.session.execute(text("DROP TABLE client_claims CASCADE"))
        sess.session.execute(text("DROP TABLE client_cors_origins CASCADE"))
        sess.session.execute(text("DROP TABLE client_grant_types CASCADE"))
        sess.session.execute(text("DROP TABLE client_id_restrictions CASCADE"))
        sess.session.execute(text("DROP TABLE client_post_logout_redirect_uris CASCADE"))
        sess.session.execute(text("DROP TABLE client_redirect_uris CASCADE"))
        sess.session.execute(text("DROP TABLE client_scopes CASCADE"))
        sess.session.execute(text("DROP TABLE client_secrets CASCADE"))
        sess.session.execute(text("DROP TABLE clients CASCADE"))
        sess.session.execute(text("DROP TABLE groups CASCADE"))
        sess.session.execute(text("DROP TABLE identity_claims CASCADE"))
        sess.session.execute(text("DROP TABLE identity_resources CASCADE"))
        sess.session.execute(text("DROP TABLE permissions CASCADE"))
        sess.session.execute(text("DROP TABLE permissions_groups CASCADE"))
        sess.session.execute(text("DROP TABLE permissions_roles CASCADE"))
        sess.session.execute(text("DROP TABLE persistent_grants CASCADE"))
        sess.session.execute(text("DROP TABLE roles CASCADE"))
        sess.session.execute(text("DROP TABLE user_claims CASCADE"))
        sess.session.execute(text("DROP TABLE user_logins CASCADE"))
        sess.session.execute(text("DROP TABLE users CASCADE"))
        sess.session.execute(text("DROP TABLE users_groups CASCADE"))
        sess.session.execute(text("DROP TABLE users_roles CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE alembic_version"))
        sess.session.commit()



if __name__ == "__main__":
    DataBasePurge.populate_database()
