import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.factory_session as sess
import src.data_access.postgresql.tables.persistent_grant as grant
from factories.data.data_for_factories import TYPES_OF_GRANTS
from factories.factory_models.client_factory import ClientFactory
from factories.factory_models.user_factory import UserFactory
import factories.data.data_for_factories as data

class PersistentGrantFactory(SQLAlchemyModelFactory):
    class Meta:
        model = grant.PersistentGrant
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("key",)

    key = factory.Faker("md5", raw_output=False)
    client_id = factory.SubFactory(ClientFactory)
    data = factory.Faker("md5", raw_output=False)
    expiration = factory.Faker("date_time")
    subject_id = factory.SubFactory(UserFactory)
    type = FuzzyChoice(TYPES_OF_GRANTS)

class PersistentGrantTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = grant.PersistentGrantType
        sqlalchemy_session = sess.session

    type_of_grant = FuzzyChoice(data.TYPES_OF_GRANTS)