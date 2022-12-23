import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.factory_session as sess
import src.data_access.postgresql.tables.client as client
import factories.data.data_for_factories as data


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.Client
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ('client_id',)

    client_id = factory.Iterator(data.CLIENT_IDS)
    absolute_refresh_token_lifetime = factory.Faker('pyint', min_value=3600, max_value=50000)
    access_token_lifetime = factory.Faker('pyint', min_value=300, max_value=10000)
    access_token_type = FuzzyChoice(['reference', 'jwt'])
    allow_access_token_via_browser = FuzzyChoice([True, False])
    allow_offline_access = factory.Faker('pybool')
    allow_plain_text_pkce = factory.Faker('pybool')
    allow_remember_consent = factory.Faker('pybool')
    always_include_user_claims_id_token = factory.Faker('pybool')
    always_send_client_claims = factory.Faker('pybool')
    authorisation_code_lifetime = factory.Faker('random_number')
    client_name = factory.Faker('user_name')
    client_uri = factory.Faker('url')
    enable_local_login = factory.Faker('pybool')
    enabled = factory.Faker('pybool')
    identity_token_lifetime = factory.Faker('random_number')
    include_jwt_id = factory.Faker('pybool')
    logo_uri = factory.Faker('url')
    logout_session_required = factory.Faker('pybool')
    logout_uri = factory.Faker('url')
    prefix_client_claims = factory.Faker('word')
    protocol_type = FuzzyChoice(['open_id_connect'])
    refresh_token_expiration = FuzzyChoice(['absolute', 'sliding'])
    refresh_token_usage = FuzzyChoice(['one_time_only', 'reuse'])
    require_client_secret = factory.Faker('pybool')
    require_consent = factory.Faker('pybool')
    require_pkce = factory.Faker('pybool')
    sliding_refresh_token_lifetime = factory.Faker('pyint', min_value=300, max_value=1296000)
    update_access_token_claims_on_refresh = FuzzyChoice([True, False])


class ClientIdRestrictionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientIdRestriction
        sqlalchemy_session = sess.session

    provider = factory.Faker('word')
    client_id = factory.SubFactory(ClientFactory)


class ClientClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientClaim
        sqlalchemy_session = sess.session

    type = factory.Faker('word')
    value = factory.Faker('word')
    client_id = factory.SubFactory(ClientFactory)


class ClientScopeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientScope
        sqlalchemy_session = sess.session

    scope = factory.Faker('sentence')
    client_id = factory.SubFactory(ClientFactory)


class ClientPostLogoutRedirectUriFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientPostLogoutRedirectUri
        sqlalchemy_session = sess.session

    post_logout_redirect_uri = factory.Faker('url')
    client_id = factory.SubFactory(ClientFactory)


class ClientCorsOriginFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientCorsOrigin
        sqlalchemy_session = sess.session

    origin = factory.Faker('sentence')
    client_id = factory.SubFactory(ClientFactory)


class ClientRedirectUriFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientRedirectUri
        sqlalchemy_session = sess.session

    redirect_uri = factory.Faker('url')
    client_id = factory.SubFactory(ClientFactory)


class ClientSecretFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientSecret
        sqlalchemy_session = sess.session

    description = factory.Faker('sentence')
    expiration = factory.Faker('random_number')
    type = factory.Faker('word')
    value = factory.Faker('word')
    client_id = factory.SubFactory(ClientFactory)


class ClientGrantTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientGrantType
        sqlalchemy_session = sess.session

    grant_type = FuzzyChoice(['code', ])
    client_id = factory.SubFactory(ClientFactory)
