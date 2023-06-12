import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.data.data_for_factories as data
import factories.factory_session as sess
import factories.factory_models.client_factory as client
import src.data_access.postgresql.tables.resources_related as resource
from factories.data.data_for_factories import (
    API_CLAIM_TYPE,
    API_SCOPE_CLAIM_TYPE,
    API_SECRET_TYPE,
)


class ApiClaimTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiClaimType
        sqlalchemy_session = sess.session

    claim_type = FuzzyChoice(data.API_CLAIM_TYPE)

class ApiScopeClaimTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiScopeClaimType
        sqlalchemy_session = sess.session

    scope_claim_type = FuzzyChoice(data.API_SCOPE_CLAIM_TYPE)

class ApiSecretsTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiSecretType
        sqlalchemy_session = sess.session

    secret_type = FuzzyChoice(data.API_SECRET_TYPE)


class ApiResourceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiResource
        sqlalchemy_session = sess.session

    description = FuzzyChoice(data.API_RESOURCES[0])
    display_name = FuzzyChoice(data.API_RESOURCES[0])
    enabled = factory.Faker("pybool")
    name = FuzzyChoice(data.API_RESOURCES[0])


class ApiSecretFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiSecret
        sqlalchemy_session = sess.session

    description = FuzzyChoice(data.API_SECRET[0])
    expiration = FuzzyChoice(data.API_SECRET[0])
    value = FuzzyChoice(data.API_SECRET[0])
    secret_type_id = FuzzyChoice(data.API_SECRET[0])
    api_resources_id = factory.SubFactory(ApiResourceFactory)
    secret_type_id = factory.SubFactory(ApiSecretsTypeFactory)

class ApiClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiClaim
        sqlalchemy_session = sess.session

    api_resources_id = factory.SubFactory(ApiResourceFactory)
    type = FuzzyChoice(API_CLAIM_TYPE)


class ApiScopeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiScope
        sqlalchemy_session = sess.session

    api_resources_id = factory.SubFactory(ApiResourceFactory)
    description = factory.Faker("sentence")
    name = factory.Faker("word")
    display_name = factory.Faker("word")
    emphasize = factory.Faker("pybool")
    required = factory.Faker("pybool")
    show_in_discovery_document = factory.Faker("pybool")


class ApiScopeClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiScopeClaim
        sqlalchemy_session = sess.session

    api_scopes_id = factory.SubFactory(ApiScopeFactory)
    scope_claim_type_id = factory.SubFactory(ApiScopeClaimTypeFactory)

class ClientScopeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ClientScope
        sqlalchemy_session = sess.session

    client_id = factory.SubFactory(client.ClientFactory)
    resource_id = factory.SubFactory(ApiResourceFactory)
    scope_id = factory.SubFactory(ApiScopeFactory)
    claim_id = factory.SubFactory(ApiClaimTypeFactory)