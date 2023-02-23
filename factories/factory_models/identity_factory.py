import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.data.data_for_factories as data
import factories.factory_session as sess
import src.data_access.postgresql.tables.identity_resource as identity
from factories.data.data_for_factories import (
    IDENTITY_PROVIDERS
)

class IdentityProviderFactory(SQLAlchemyModelFactory):
    class Meta:
        model = identity.IdentityProvider
        sqlalchemy_session = sess.session
    
    name = factory.Faker("word")
    auth_endpoint_link =  factory.Faker("word")
    token_endpoint_link =  factory.Faker("word")
    userinfo_link = factory.Faker("word")
    internal_redirect_uri = factory.Faker("word")
    
