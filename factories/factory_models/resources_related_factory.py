import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.factory_session as sess
import src.data_access.postgresql.tables.resources_related as resource
from factories.data.data_for_factories import (
    API_CLAIM_TYPE,
    API_SCOPE_CLAIM_TYPE,
    API_SECRET_TYPE,
)


class ApiResourceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiResource
        sqlalchemy_session = sess.session

    description = factory.Faker("sentence")
    display_name = factory.Faker("word")
    enabled = factory.Faker("pybool")
    name = factory.Faker("word")


class ApiSecretFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.ApiSecret
        sqlalchemy_session = sess.session

    api_resources_id = factory.SubFactory(ApiResourceFactory)
    description = factory.Faker("sentence")
    expiration = factory.Faker("date_time")
    type = FuzzyChoice(API_SECRET_TYPE)
    value = factory.Faker("word")


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
    type = FuzzyChoice(API_SCOPE_CLAIM_TYPE)
