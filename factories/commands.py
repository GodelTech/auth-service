import factory
from sqlalchemy import text

import factories.data.data_for_factories as data
import factories.factory_models.client_factory as cl_factory
import factories.factory_models.user_factory as user_factory
import factories.factory_models.resources_related_factory as res_factory
import factories.factory_models.persistent_grant_factory as grant_factory
import factories.factory_session as sess


factory.random.reseed_random(0)


class DataBasePopulation:
    @classmethod
    def populate_database(cls):
        # clean data from the tables in database
        cls.clean_data_from_database()

        # populate database
        cls.populate_user_claim_types_table()
        cls.populate_api_claim_types_table()
        cls.populate_api_secrets_types_table()
        cls.populate_api_scope_claim_types_table()
        cls.populate_persistent_grant_types_table()
        cls.populate_client_table()
        cls.populate_user_table()
        cls.populate_user_claims_table()
        # cls.populate_client_post_logout_redirect_uri()
        # cls.populate_client_secrets()
        # cls.populate_client_redirect_uri()
        # cls.populate_roles()

    @classmethod
    def clean_data_from_database(cls):
        sess.session.execute(text("TRUNCATE TABLE user_claim_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE api_claim_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE api_scope_claim_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE api_secrets_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE persistent_grant_types RESTART IDENTITY CASCADE"))
        
        sess.session.execute(text("TRUNCATE TABLE persistent_grants RESTART IDENTITY"))
        sess.session.execute(text("TRUNCATE TABLE client_secrets RESTART IDENTITY"))
        sess.session.execute(text("TRUNCATE TABLE user_claims RESTART IDENTITY"))
        sess.session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE clients RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE roles RESTART IDENTITY CASCADE"))

        sess.session.execute(text("TRUNCATE TABLE access_token_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE protocol_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE refresh_token_expiration_types RESTART IDENTITY CASCADE"))
        sess.session.execute(text("TRUNCATE TABLE refresh_token_usage_types RESTART IDENTITY CASCADE"))

        sess.session.commit()

    @classmethod
    def populate_user_claim_types_table(cls):
        for val in data.USER_CLAIM_TYPE:
            type_of_claim = user_factory.UserClaimTypeFactory(type_of_claim=val)
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    # @classmethod
    # def populate_access_token_types_table(cls):
    #     for val in data.ACCESS_TOKEN_TYPES:
    #         type = cl_factory.AccessTokenTypeFactory(type=val)
    #         cl_factory.sess.session.commit()
    #         cl_factory.sess.session.close()

    @classmethod
    def populate_api_claim_types_table(cls):
        for val in data.API_CLAIM_TYPE:
            claim_type = res_factory.ApiClaimTypeFactory(claim_type=val)
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_api_secrets_types_table(cls):
        for val in data.API_SECRET_TYPE:
            secret_type = res_factory.ApiSecretsTypeFactory(secret_type=val)
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_api_scope_claim_types_table(cls):
        for val in data.API_SCOPE_CLAIM_TYPE:
            scope_claim_type = res_factory.ApiScopeClaimTypeFactory(scope_claim_type=val)
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_persistent_grant_types_table(cls):
        for val in data.TYPES_OF_GRANTS:
            type_of_grant = grant_factory.PersistentGrantTypeFactory(type_of_grant=val)
            grant_factory.sess.session.commit()
            grant_factory.sess.session.close()



    @classmethod
    def populate_client_table(cls):

        # Firstly populating types and usages that are needed for the Client 
        for i in range(len(data.ACCESS_TOKEN_TYPES)):
            token = cl_factory.AccessTokenTypeFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

        for i in range(len(data.PROTOCOL_TYPES)):
            token = cl_factory.ProtocolTypeFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()
        
        for i in range(len(data.REFRESH_TOKEN_EXPIRATION_TYPES)):
            token = cl_factory.RefreshTokenExpirationTypeFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

        for i in range(len(data.REFRESH_TOKEN_USAGE)):
            token = cl_factory.RefreshTokenUsageTypeFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

        # Finally populating CLient
        for i in range(len(data.CLIENT_IDS)):
            client = cl_factory.ClientFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_user_table(cls):
        for i in range(len(data.CLIENT_USERNAMES)):
            user = user_factory.UserFactory()
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_user_claims_table(cls):
        for key, val in data.DEFAULT_USER_CLAIMS.items():
            claim = user_factory.UserClaimFactory(
                user_id=1, claim_type_id=key, claim_value=val
            )
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_client_post_logout_redirect_uri(cls):
        for item in data.CLIENT_IDS:
            uri = cl_factory.ClientPostLogoutRedirectUriFactory(client_id=item)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_client_secrets(cls):
        for client_id, secret in data.CLIENT_SECRETS.items():
            sec = cl_factory.ClientSecretFactory(client_id=client_id, value=secret)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_client_redirect_uri(cls):
        for item in data.CLIENT_IDS:
            uri = cl_factory.ClientRedirectUriFactory(client_id=item, redirect_uri="https://www.google.com/")
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_roles(cls):
        for role in data.ROLES:
            user_factory.RoleFactory(name=role)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()


if __name__ == "__main__":
    DataBasePopulation.populate_database()
