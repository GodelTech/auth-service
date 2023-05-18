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
    def populate_database(cls) -> None:
        # clean data from the tables in database
        cls.clean_data_from_database()

        # populate database
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
        cls.reset_autoincrement()
        # cls.get_table_info(print_bool = True)

    @classmethod
    def populate_user_password_table(cls) -> None:
        # from src.business_logic.services.password import PasswordHash

        for i in range(len(data.CLIENT_USERNAMES)):
            password = user_factory.UserPasswordFactory()
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def clean_data_from_database(cls) -> None:
        tables = sess.engine.table_names()
        excluded_table = 'alembic_version'
        for table_name in tables:
            if table_name != excluded_table:
                sess.session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
        sess.session.commit()

    
    @classmethod
    def get_table_info(cls, table_names = [], print_bool = True, auto_inc_next=True):
        table_info = []
        part_of_sql = ''
        if auto_inc_next==True:
            part_of_sql = 'nextval'
        else:
            part_of_sql = 'currval'

        if table_names == []:
            table_names = sess.engine.table_names()

        for table_name in table_names:
            table_dict = {"name": table_name}
            try:
                auto_increment_value = sess.session.execute(f"SELECT {part_of_sql}('{table_name}_id_seq')")
                auto_increment_value = auto_increment_value.fetchone()
            except:
                auto_increment_value = ['error']
            
            sess.session.rollback()
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            count_result =  sess.session.execute(count_query).fetchone()
            table_dict["number_of_inst"] = count_result[0] if count_result else None
            table_dict["auto_increment"] = auto_increment_value[0] if auto_increment_value else None
            table_dict["diff"] = table_dict["auto_increment"] - table_dict["number_of_inst"] if auto_increment_value[0]!= 'error' else None

            table_info.append(table_dict)
        return table_info


    @classmethod
    def reset_autoincrement(cls, print_bool = True):
        table_info = cls.get_table_info()
        table_names = []
        for i in table_info:
            if i['diff'] is not None and i['diff']!=1:
               # if print_bool:
                # print(i)
                sess.session.execute(f"SELECT setval('{i['name']}_id_seq', {i['number_of_inst']});")
                table_names.append(i['name'])
        sess.session.commit()

    @classmethod
    def populate_user_claim_types_table(cls) -> None:
        for val in data.USER_CLAIM_TYPE:
            type_of_claim = user_factory.UserClaimTypeFactory(type_of_claim=val)
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_identity_providers_table(cls) -> None:
        for val in data.IDENTITY_PROVIDERS:
            tp = id_factory.IdentityProviderFactory(**val)
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_api_claim_types_table(cls) -> None:
        for val in data.API_CLAIM_TYPE:
            claim_type = res_factory.ApiClaimTypeFactory(claim_type=val)
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_api_secrets_types_table(cls) -> None:
        for val in data.API_SECRET_TYPE:
            secret_type = res_factory.ApiSecretsTypeFactory(secret_type=val)
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_api_scope_claim_types_table(cls) -> None:
        for val in data.API_SCOPE_CLAIM_TYPE:
            scope_claim_type = res_factory.ApiScopeClaimTypeFactory(
                scope_claim_type=val
            )
            res_factory.sess.session.commit()
            res_factory.sess.session.close()

    @classmethod
    def populate_persistent_grant_types_table(cls) -> None:
        for val in data.TYPES_OF_GRANTS:
            type_of_grant = grant_factory.PersistentGrantTypesFactory(
                type_of_grant=val
            )
            grant_factory.sess.session.commit()
            grant_factory.sess.session.close()

    @classmethod
    def populate_client_table(cls) -> None:
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

        # Finally, populating Client
        for i in range(len(data.CLIENT_IDS)):
            client = cl_factory.ClientFactory()
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_user_table(cls) -> None:
        for i in range(len(data.CLIENT_USERNAMES)):
            user = user_factory.UserFactory(password_hash_id=i + 1)
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_user_claims_table(cls) -> None:
        for key, val in data.DEFAULT_USER_CLAIMS.items():
            claim = user_factory.UserClaimFactory(
                user_id=1, claim_type_id=key, claim_value=val
            )
            user_factory.sess.session.commit()
            user_factory.sess.session.close()

    @classmethod
    def populate_client_post_logout_redirect_uri(cls) -> None:
        for i in range(len(data.POST_LOGOUT_REDIRECT_URL)):
            uri = cl_factory.ClientPostLogoutRedirectUriFactory(
                client_id=i + 1,
                post_logout_redirect_uri=data.POST_LOGOUT_REDIRECT_URL[i],
            )
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_client_secrets(cls) -> None:
        for client_id, secret in data.CLIENT_SECRETS.items():
            sec = cl_factory.ClientSecretFactory(
                client_id=client_id, value=secret
            )
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_client_scopes(cls) -> None:
        for client_id, scope in data.CLIENT_SCOPES.items():
            sec = cl_factory.ClientScopeFactory(
                client_id=client_id, scope=scope
            )
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_client_redirect_uri(cls) -> None:
        for item in range(len(data.CLIENT_IDS)):
            uri = cl_factory.ClientRedirectUriFactory(
                client_id=item + 1, redirect_uri="https://www.google.com/"
            )
            cl_factory.sess.session.commit()
            cl_factory.sess.session.close()

    @classmethod
    def populate_roles(cls) -> None:
        for role in data.ROLES:
            user_factory.RoleFactory(name=role)
            user_factory.sess.session.commit()  # cl/user?
            user_factory.sess.session.close()

    @classmethod
    def populate_grants(cls) -> None:
        for grant_type in data.TYPES_OF_GRANTS:
            grant_factory.PersistentGrantTypesFactory()
            grant_factory.sess.session.commit()
            grant_factory.sess.session.close()

        for grant in data.TYPES_OF_GRANTS:
            grant_factory.PersistentGrantFactory()
            grant_factory.sess.session.commit()
            grant_factory.sess.session.close()


if __name__ == "__main__":
    DataBasePopulation.populate_database()
