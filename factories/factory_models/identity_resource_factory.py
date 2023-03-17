import factory
from factory.alchemy import SQLAlchemyModelFactory

import factories.factory_session as sess
import src.data_access.postgresql.tables.identity_resource as resource


class IdentityResourceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.IdentityResource
        sqlalchemy_session = sess.session

    description = factory.Faker("text", max_nb_chars=456)
    display_name = factory.Faker("word")
    emphasize = factory.Faker("pybool")
    enabled = factory.Faker("pybool")
    name = factory.Faker("word")
    required = factory.Faker("pybool")
    show_in_discovery_document = factory.Faker("pybool")


class IdentityClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = resource.IdentityClaim
        sqlalchemy_session = sess.session

    identity_resource_id = factory.SubFactory(IdentityResourceFactory)
    type = factory.Faker("word")
