import factory
from sqlalchemy import text

import factories.data.data_for_factories as data
import factories.factory_models.client_factory as cl_factory
import factories.factory_models.identity_factory as id_factory
import factories.factory_models.persistent_grant_factory as grant_factory
import factories.factory_models.resources_related_factory as res_factory
import factories.factory_models.user_factory as user_factory
import factories.factory_session as sess

factory.random.reseed_random(0)


class DataBasePopulation:
    @classmethod
    def clean_and_populate(cls) -> None:
        cls.populate_database()

    @classmethod
    def populate_database(cls) -> None:
        # populate database
        cls.clean_data_from_database()
        cls.populate_response_types_table()
        cls.populate_identity_providers_table()
        cls.populate_user_claim_types_table()
        cls.populate_api_claim_types_table()
        cls.populate_api_secrets_types_table()
        cls.populate_api_scope_claim_types_table()
        cls.populate_persistent_grant_types_table()
        cls.populate_client_table()
        cls.populate_user_password_table()
        cls.populate_user_table()

        cls.populate_user_claims_table()
        cls.populate_client_post_logout_redirect_uri()
        cls.populate_client_secrets()
        cls.populate_client_scopes()
        cls.populate_client_redirect_uri()
        cls.populate_roles()
        cls.populate_grants()
        sess.session.commit()
        sess.session.close()

    @classmethod
    def populate_user_password_table(cls) -> None:
        # from src.business_logic.services.password import PasswordHash

        for i in range(len(data.CLIENT_HASH_PASSWORDS)):
            user_factory.UserPasswordFactory()

    @classmethod
    def clean_data_from_database(cls) -> None:
        result = sess.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        table_names = [row[0] for row in result]
        excluded_table = 'alembic_version'
        for table_name in table_names:
            if table_name != excluded_table:
                sess.session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        sess.session.flush()
        
        

    @classmethod
    def populate_user_claim_types_table(cls) -> None:
        for val in data.USER_CLAIM_TYPE:
            user_factory.UserClaimTypeFactory(type_of_claim=val)

    @classmethod
    def populate_identity_providers_table(cls) -> None:
        for val in data.IDENTITY_PROVIDERS:
            id_factory.IdentityProviderFactory(**val)

    @classmethod
    def populate_api_claim_types_table(cls) -> None:
        for val in data.API_CLAIM_TYPE:
            res_factory.ApiClaimTypeFactory(claim_type=val)

    @classmethod
    def populate_api_secrets_types_table(cls) -> None:
        for val in data.API_SECRET_TYPE:
            res_factory.ApiSecretsTypeFactory(secret_type=val)

    @classmethod
    def populate_api_scope_claim_types_table(cls) -> None:
        for val in data.API_SCOPE_CLAIM_TYPE:
            res_factory.ApiScopeClaimTypeFactory(
                scope_claim_type=val
            )

    @classmethod
    def populate_persistent_grant_types_table(cls) -> None:
        for val in data.TYPES_OF_GRANTS:
            grant_factory.PersistentGrantTypesFactory(
                type_of_grant=val
            )

    @classmethod
    def populate_response_types_table(cls) -> None:
        for val in data.RESPONSE_TYPES:
            smth = cl_factory.ResponseTypeFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_response_types_table(cls) -> None:
        for val in data.RESPONSE_TYPES:
            smth = cl_factory.ResponseTypeFactory()

    @classmethod
    def populate_client_table(cls) -> None:
        # Firstly populating types and usages that are needed for the Client
        for i in range(len(data.ACCESS_TOKEN_TYPES)):
            cl_factory.AccessTokenTypeFactory()

        for i in range(len(data.PROTOCOL_TYPES)):
            cl_factory.ProtocolTypeFactory()

        for i in range(len(data.REFRESH_TOKEN_EXPIRATION_TYPES)):
            cl_factory.RefreshTokenExpirationTypeFactory()

        for i in range(len(data.REFRESH_TOKEN_USAGE)):
            cl_factory.RefreshTokenUsageTypeFactory()

        # Finally, populating Client
        for id, client_id in data.CLIENT_IDS.items():
            cl_factory.ClientFactory(client_id=client_id)

    @classmethod
    def populate_user_table(cls) -> None:
        for client_id, _ in data.CLIENT_USERNAMES.items():
            user_factory.UserFactory(password_hash_id=client_id)

    @classmethod
    def populate_user_claims_table(cls) -> None:
        for key, val in data.DEFAULT_USER_CLAIMS.items():
            user_factory.UserClaimFactory(
                user_id=1, claim_type_id=key, claim_value=val
            )

    @classmethod
    def populate_client_post_logout_redirect_uri(cls) -> None:
        for client_id, post_logout_redirect_uri in data.POST_LOGOUT_REDIRECT_URL.items():
            cl_factory.ClientPostLogoutRedirectUriFactory(
                client_id=client_id,
                post_logout_redirect_uri=post_logout_redirect_uri,
            )

    @classmethod
    def populate_client_secrets(cls) -> None:
        for client_id, secret in data.CLIENT_SECRETS.items():
            cl_factory.ClientSecretFactory(
                client_id=client_id, value=secret
            )

    @classmethod
    def populate_client_scopes(cls) -> None:
        for client_id, scope in data.CLIENT_SCOPES.items():
            cl_factory.ClientScopeFactory(
                client_id=client_id, scope=scope
            )

    @classmethod
    def populate_client_redirect_uri(cls) -> None:
        for client_id, client_name in data.CLIENT_IDS.items():
            cl_factory.ClientRedirectUriFactory(
                client_id=client_id, redirect_uri="https://www.google.com/"
            )

    @classmethod
    def populate_roles(cls) -> None:
        for role in data.ROLES:
            user_factory.RoleFactory(name=role)

    @classmethod
    def populate_grants(cls) -> None:

        # For what do we need to populate persistent_grant_types table here?
        # It's been already populated in populate_persistent_grant_types_table method
        # It is not being added twice only because of sqlalchemy_get_or_create = ("type_of_grant",) line
        # in PersistentGrantTypesFactory class

        # for grant_type in data.TYPES_OF_GRANTS:
        #     grant_factory.PersistentGrantTypesFactory()
        #     grant_factory.
        #     grant_factory.

        # for grant in data.TYPES_OF_GRANTS:
        for i in range(2):
            grant_factory.PersistentGrantFactory()


if __name__ == "__main__":
    DataBasePopulation.clean_and_populate()
