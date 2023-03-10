import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.data.data_for_factories as data
import factories.factory_session as sess
import src.data_access.postgresql.tables.persistent_grant as grant
from factories.data.data_for_factories import TYPES_OF_GRANTS
from factories.factory_models.client_factory import ClientFactory
from factories.factory_models.user_factory import UserFactory


class PersistentGrantFactory(SQLAlchemyModelFactory):
    class Meta:
        model = grant.PersistentGrant
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("key",)

    class Params:
        client = factory.SubFactory(ClientFactory)
        user = factory.SubFactory(UserFactory)

    key = factory.Faker("md5", raw_output=False)
    client_id = factory.SelfAttribute("client.id")
    grant_data = factory.Faker("md5", raw_output=False)
    expiration = factory.Faker("pyint", min_value=600, max_value=90000)
    user_id = factory.SelfAttribute("user.id")
    persistent_grant_type_id = factory.Faker("pyint", min_value=1, max_value=2)


class PersistentGrantTypesFactory(SQLAlchemyModelFactory):
    class Meta:
        model = grant.PersistentGrantType
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("type_of_grant",)

    id = factory.Sequence(lambda n: n + 1)
    type_of_grant = factory.Iterator(["authorization_code", "refresh_token"])
